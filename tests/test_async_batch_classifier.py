"""
Integration tests for async batch classification endpoints
"""

import pytest
import json
import time
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import app
from model import Session, BatchJob, JobStatus
from schemas.batch_job import BatchClassifyAsyncRequest, BatchClassifyAsyncResponse, BatchJobStatusResponse


@pytest.fixture
def client():
    """Create test client"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def sample_transactions():
    """Sample transaction data for testing"""
    return [
        {
            "date": "2024-01-15T00:00:00",
            "description": "Grocery shopping at Whole Foods",
            "value": 150.50,
            "user": "John Doe",
            "classification": None
        },
        {
            "date": "2024-01-16T00:00:00",
            "description": "Gas station fuel",
            "value": 45.00,
            "user": "John Doe",
            "classification": None
        }
    ]


@pytest.fixture(autouse=True)
def cleanup_database():
    """Clean up test jobs after each test"""
    yield
    # Cleanup after test
    session = Session()
    test_jobs = session.query(BatchJob).all()
    for job in test_jobs:
        session.delete(job)
    session.commit()
    session.close()


class TestAsyncBatchClassifier:
    """Test suite for async batch classification"""
    
    def test_post_batch_classify_async_returns_202_and_job_id(self, client, sample_transactions):
        """Test POST endpoint returns 202 Accepted with job ID"""
        response = client.post(
            '/batch-classify-async',
            data=json.dumps({"transactions": sample_transactions}),
            content_type='application/json'
        )
        
        assert response.status_code == 202
        data = json.loads(response.data)
        assert 'jobId' in data
        assert len(data['jobId']) == 36  # UUID length with hyphens
    
    def test_post_batch_classify_async_creates_database_entry(self, client, sample_transactions):
        """Test POST endpoint creates job in database"""
        response = client.post(
            '/batch-classify-async',
            data=json.dumps({"transactions": sample_transactions}),
            content_type='application/json'
        )
        
        data = json.loads(response.data)
        job_id = data['jobId']
        
        # Check database
        session = Session()
        batch_job = session.query(BatchJob).filter(BatchJob.id == job_id).first()
        
        assert batch_job is not None
        assert batch_job.status == JobStatus.PENDING
        assert batch_job.transactions_input is not None
        
        session.close()
    
    def test_get_batch_job_status_pending(self, client, sample_transactions):
        """Test GET endpoint with pending job"""
        # Create job
        post_response = client.post(
            '/batch-classify-async',
            data=json.dumps({"transactions": sample_transactions}),
            content_type='application/json'
        )
        job_id = json.loads(post_response.data)['jobId']
        
        # Get status
        response = client.get(f'/batch-jobs/{job_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'pending'
        assert 'transactions' not in data or data['transactions'] is None
    
    def test_get_batch_job_status_processing(self, client):
        """Test GET endpoint with processing job"""
        # Create job manually in database with processing status
        session = Session()
        batch_job = BatchJob(
            transactions_input=json.dumps([{"test": "data"}]),
            status=JobStatus.PROCESSING
        )
        session.add(batch_job)
        session.commit()
        job_id = batch_job.id
        session.close()
        
        # Get status
        response = client.get(f'/batch-jobs/{job_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'processing'
    
    def test_get_batch_job_status_completed_with_results(self, client, sample_transactions):
        """Test GET endpoint with completed job returns results"""
        # Create completed job manually
        classified = sample_transactions.copy()
        classified[0]['classification'] = 'Food & Groceries'
        classified[1]['classification'] = 'Transportation'
        
        session = Session()
        batch_job = BatchJob(
            transactions_input=json.dumps(sample_transactions),
            status=JobStatus.COMPLETED
        )
        batch_job.transactions_output = json.dumps(classified)
        session.add(batch_job)
        session.commit()
        job_id = batch_job.id
        session.close()
        
        # Get status
        response = client.get(f'/batch-jobs/{job_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'completed'
        assert 'transactions' in data
        assert len(data['transactions']) == 2
        assert data['transactions'][0]['classification'] == 'Food & Groceries'
    
    def test_get_batch_job_status_completed_deletes_job(self, client):
        """Test GET endpoint deletes job after fetching completed results"""
        # Create completed job
        session = Session()
        batch_job = BatchJob(
            transactions_input=json.dumps([]),
            status=JobStatus.COMPLETED
        )
        batch_job.transactions_output = json.dumps([])
        session.add(batch_job)
        session.commit()
        job_id = batch_job.id
        session.close()
        
        # First fetch - should succeed
        response1 = client.get(f'/batch-jobs/{job_id}')
        assert response1.status_code == 200
        
        # Second fetch - should return 404
        response2 = client.get(f'/batch-jobs/{job_id}')
        assert response2.status_code == 404
    
    def test_get_batch_job_status_failed_with_error_message(self, client):
        """Test GET endpoint with failed job returns error message"""
        # Create failed job
        session = Session()
        batch_job = BatchJob(
            transactions_input=json.dumps([]),
            status=JobStatus.FAILED
        )
        batch_job.error_message = "External API unavailable"
        session.add(batch_job)
        session.commit()
        job_id = batch_job.id
        session.close()
        
        # Get status
        response = client.get(f'/batch-jobs/{job_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'failed'
        assert data['message'] == "External API unavailable"
    
    def test_get_batch_job_status_not_found(self, client):
        """Test GET endpoint with non-existent job ID returns 404"""
        response = client.get('/batch-jobs/non-existent-job-id')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'message' in data
    
    def test_post_batch_classify_async_with_invalid_data(self, client):
        """Test POST endpoint with invalid data returns 400"""
        response = client.post(
            '/batch-classify-async',
            data=json.dumps({"invalid": "data"}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
    
    def test_post_batch_classify_async_with_empty_transactions(self, client):
        """Test POST endpoint with empty transactions list"""
        response = client.post(
            '/batch-classify-async',
            data=json.dumps({"transactions": []}),
            content_type='application/json'
        )
        
        # Should still create job (edge case)
        assert response.status_code == 202


class TestRetryLogic:
    """Test retry logic for external API calls"""
    
    def test_retry_decorator_retries_on_failure(self):
        """Test retry decorator retries correct number of times"""
        from kafka.utils import retry_with_backoff
        
        call_count = 0
        
        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        def failing_function():
            nonlocal call_count
            call_count += 1
            raise Exception("Test failure")
        
        with pytest.raises(Exception):
            failing_function()
        
        assert call_count == 3
    
    def test_retry_decorator_succeeds_on_second_attempt(self):
        """Test retry decorator succeeds after initial failure"""
        from kafka.utils import retry_with_backoff
        
        call_count = 0
        
        @retry_with_backoff(max_retries=3, initial_delay=0.1)
        def sometimes_failing_function():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise Exception("Test failure")
            return "success"
        
        result = sometimes_failing_function()
        
        assert result == "success"
        assert call_count == 2


class TestJobCleanup:
    """Test job cleanup functionality"""
    
    def test_cleanup_removes_old_jobs(self):
        """Test cleanup script removes jobs older than 24 hours"""
        from kafka.job_cleanup import cleanup_old_jobs
        from datetime import datetime, timedelta
        
        # Create old job
        session = Session()
        old_job = BatchJob(
            transactions_input=json.dumps([]),
            status=JobStatus.COMPLETED
        )
        old_job.created_at = datetime.now() - timedelta(hours=25)
        session.add(old_job)
        session.commit()
        old_job_id = old_job.id
        session.close()
        
        # Run cleanup
        deleted = cleanup_old_jobs(max_age_hours=24)
        
        assert deleted == 1
        
        # Verify job is gone
        session = Session()
        job = session.query(BatchJob).filter(BatchJob.id == old_job_id).first()
        assert job is None
        session.close()
    
    def test_cleanup_keeps_recent_jobs(self):
        """Test cleanup script keeps recent jobs"""
        from kafka.job_cleanup import cleanup_old_jobs
        
        # Create recent job
        session = Session()
        recent_job = BatchJob(
            transactions_input=json.dumps([]),
            status=JobStatus.PENDING
        )
        session.add(recent_job)
        session.commit()
        recent_job_id = recent_job.id
        session.close()
        
        # Run cleanup
        deleted = cleanup_old_jobs(max_age_hours=24)
        
        assert deleted == 0
        
        # Verify job still exists
        session = Session()
        job = session.query(BatchJob).filter(BatchJob.id == recent_job_id).first()
        assert job is not None
        session.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

