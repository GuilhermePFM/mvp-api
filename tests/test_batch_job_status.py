import pytest
from unittest.mock import patch, MagicMock
import json
from datetime import datetime
from app import app
from model import BatchJob, JobStatus
import sys
import os


# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestGetBatchJobStatus:
    """Test suite for the GET /batch-jobs/{job_id} endpoint"""
    
    @patch('apis.batch_classifier.Session')
    def test_get_batch_job_status_pending(self, mock_session_class, client):
        """Test fetching a job with PENDING status"""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_job = MagicMock()
        mock_job.id = "test-job-id-123"
        mock_job.status = JobStatus.PENDING
        mock_job.transactions_output = None
        mock_job.error_message = None
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        # Make request
        response = client.get('/batch-jobs/test-job-id-123')
        
        # Assertions
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'pending'
        assert 'transactions' not in response_data or response_data.get('transactions') is None
        assert 'message' not in response_data or response_data.get('message') is None
        
        # Verify session was closed
        mock_session.close.assert_called_once()
    
    @patch('apis.batch_classifier.Session')
    def test_get_batch_job_status_processing(self, mock_session_class, client):
        """Test fetching a job with PROCESSING status"""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_job = MagicMock()
        mock_job.id = "test-job-id-456"
        mock_job.status = JobStatus.PROCESSING
        mock_job.transactions_output = None
        mock_job.error_message = None
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        # Make request
        response = client.get('/batch-jobs/test-job-id-456')
        
        # Assertions
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'processing'
        assert 'transactions' not in response_data or response_data.get('transactions') is None
        
        # Verify session was closed
        mock_session.close.assert_called_once()
    
    @patch('apis.batch_classifier.Session')
    def test_get_batch_job_status_completed_with_results(self, mock_session_class, client):
        """Test fetching a completed job with results"""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Sample transaction results
        transactions_output = [
            {
                "date": "2024-01-15T10:30:00",
                "description": "Supermarket purchase",
                "value": 150.50,
                "user": "test_user",
                "classification": "Alimentação cotidiana"
            },
            {
                "date": "2024-01-16T14:20:00",
                "description": "Gas station",
                "value": 80.00,
                "user": "test_user",
                "classification": "Transporte"
            }
        ]
        
        mock_job = MagicMock()
        mock_job.id = "test-job-id-completed"
        mock_job.status = JobStatus.COMPLETED
        mock_job.transactions_output = json.dumps(transactions_output)
        mock_job.error_message = None
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        # Make request
        response = client.get('/batch-jobs/test-job-id-completed')
        
        # Assertions
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'completed'
        assert 'transactions' in response_data
        assert len(response_data['transactions']) == 2
        assert response_data['transactions'][0]['classification'] == 'Alimentação cotidiana'
        assert response_data['transactions'][1]['classification'] == 'Transporte'
        
        # Verify job was deleted after successful fetch
        mock_session.delete.assert_called_once_with(mock_job)
        mock_session.commit.assert_called_once()
        mock_session.close.assert_called_once()
    
    @patch('apis.batch_classifier.Session')
    def test_get_batch_job_status_completed_no_results(self, mock_session_class, client):
        """Test fetching a completed job with no results"""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_job = MagicMock()
        mock_job.id = "test-job-id-no-results"
        mock_job.status = JobStatus.COMPLETED
        mock_job.transactions_output = None  # No results
        mock_job.error_message = None
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        # Make request
        response = client.get('/batch-jobs/test-job-id-no-results')
        
        # Assertions
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'completed'
        # transactions field should not be populated if no output
        assert 'transactions' not in response_data or response_data.get('transactions') is None
        
        # Verify job was still deleted
        mock_session.delete.assert_called_once_with(mock_job)
        mock_session.commit.assert_called_once()
    
    @patch('apis.batch_classifier.Session')
    def test_get_batch_job_status_failed_with_error(self, mock_session_class, client):
        """Test fetching a failed job with error message"""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_job = MagicMock()
        mock_job.id = "test-job-id-failed"
        mock_job.status = JobStatus.FAILED
        mock_job.transactions_output = None
        mock_job.error_message = "Failed to connect to embedding API"
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        # Make request
        response = client.get('/batch-jobs/test-job-id-failed')
        
        # Assertions
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'failed'
        assert response_data['message'] == "Failed to connect to embedding API"
        
        # Verify job was NOT deleted for failed status
        mock_session.delete.assert_not_called()
        mock_session.close.assert_called_once()
    
    @patch('apis.batch_classifier.Session')
    def test_get_batch_job_status_failed_no_error_message(self, mock_session_class, client):
        """Test fetching a failed job without specific error message"""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_job = MagicMock()
        mock_job.id = "test-job-id-failed-no-msg"
        mock_job.status = JobStatus.FAILED
        mock_job.transactions_output = None
        mock_job.error_message = None
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        # Make request
        response = client.get('/batch-jobs/test-job-id-failed-no-msg')
        
        # Assertions
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'failed'
        assert response_data['message'] == "Classification failed"  # Default message
    
    @patch('apis.batch_classifier.Session')
    def test_get_batch_job_status_not_found(self, mock_session_class, client):
        """Test fetching a non-existent job"""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        # Simulate job not found
        mock_session.query.return_value.filter.return_value.first.return_value = None
        
        # Make request
        response = client.get('/batch-jobs/non-existent-job-id')
        
        # Assertions
        assert response.status_code == 404
        response_data = json.loads(response.data)
        assert 'message' in response_data
        assert 'non-existent-job-id' in response_data['message']
        assert 'not found' in response_data['message'].lower()
        
        # Verify session was closed
        mock_session.close.assert_called_once()
    
    @patch('apis.batch_classifier.Session')
    def test_get_batch_job_status_database_error(self, mock_session_class, client):
        """Test handling database errors gracefully"""
        # Setup mock to raise exception
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        mock_session.query.side_effect = Exception("Database connection error")
        
        # Make request
        response = client.get('/batch-jobs/test-job-id-error')
        
        # Assertions
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'message' in response_data
        assert 'Could not fetch job status' in response_data['message']
    
    @patch('apis.batch_classifier.Session')
    def test_get_batch_job_status_invalid_json_in_output(self, mock_session_class, client):
        """Test handling invalid JSON in transactions_output"""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        mock_job = MagicMock()
        mock_job.id = "test-job-id-invalid-json"
        mock_job.status = JobStatus.COMPLETED
        mock_job.transactions_output = "invalid json {{"  # Invalid JSON
        mock_job.error_message = None
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        # Make request
        response = client.get('/batch-jobs/test-job-id-invalid-json')
        
        # Assertions
        assert response.status_code == 500
        response_data = json.loads(response.data)
        assert 'message' in response_data
        assert 'Could not fetch job status' in response_data['message']
    
    @patch('apis.batch_classifier.Session')
    def test_get_batch_job_status_uuid_format(self, mock_session_class, client):
        """Test with a properly formatted UUID"""
        # Setup mock
        mock_session = MagicMock()
        mock_session_class.return_value = mock_session
        
        uuid_job_id = "41d2f0bf-33f7-46c8-848c-ca66de82b463"
        
        mock_job = MagicMock()
        mock_job.id = uuid_job_id
        mock_job.status = JobStatus.PENDING
        mock_job.transactions_output = None
        mock_job.error_message = None
        
        mock_session.query.return_value.filter.return_value.first.return_value = mock_job
        
        # Make request with UUID format
        response = client.get(f'/batch-jobs/{uuid_job_id}')
        
        # Assertions
        assert response.status_code == 200
        response_data = json.loads(response.data)
        assert response_data['status'] == 'pending'
        
        # Verify the query was called with correct job_id
        mock_session.query.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])

