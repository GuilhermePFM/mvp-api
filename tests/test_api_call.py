from machine_learning.transactions_classifier import TransactionsClassifier
from pytest import fixture
import json
from datetime import datetime
from app import app


@fixture
def client():
    """Create a test client for the Flask app"""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_batch_classifier_api_call(client):
    """Test that the /batchclassifier endpoint processes transactions correctly"""
    # Prepare test data with valid transaction structure
    test_data = {
        "transactions": [
            {
                "date": "2024-01-15T10:30:00",
                "description": "Supermarket purchase groceries",
                "value": 150.50,
                "user": "test_user",
                "classification": None
            },
            {
                "date": "2024-01-16T14:20:00",
                "description": "Gas station fuel",
                "value": 80.00,
                "user": "test_user",
                "classification": None
            },
            {
                "date": "2024-01-17T09:00:00",
                "description": "Restaurant dinner",
                "value": 120.75,
                "user": "test_user",
                "classification": None
            }
        ]
    }
    
    # Make POST request to the batch classifier endpoint
    response = client.post(
        '/batchclassifier',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # Verify the response
    assert response.status_code == 200, f"Expected status code 200, got {response.status_code}"
    
    # Parse response data
    response_data = json.loads(response.data)
    
    # Verify response structure
    assert 'transactions' in response_data, "Response should contain 'transactions' key"
    assert len(response_data['transactions']) == 3, "Should return 3 classified transactions"
    
    # Verify each transaction has classification
    for transaction in response_data['transactions']:
        assert 'classification' in transaction, "Each transaction should have a classification"
        assert transaction['classification'] is not None, "Classification should not be None"
        assert 'date' in transaction, "Transaction should have date field"
        assert 'description' in transaction, "Transaction should have description field"
        assert 'value' in transaction, "Transaction should have value field"


def test_batch_classifier_api_empty_list(client):
    """Test that the API handles empty transaction list"""
    test_data = {
        "transactions": []
    }
    
    response = client.post(
        '/batchclassifier',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # Should handle empty list gracefully
    assert response.status_code in [200, 400], "Should return valid status code for empty list"


def test_batch_classifier_api_invalid_data(client):
    """Test that the API handles invalid data properly"""
    test_data = {
        "transactions": [
            {
                "date": "2024-01-15T10:30:00",
                "description": "Test transaction"
                # Missing required 'value' field
            }
        ]
    }
    
    response = client.post(
        '/batchclassifier',
        data=json.dumps(test_data),
        content_type='application/json'
    )
    
    # Should return error status for invalid data
    assert response.status_code in [400, 422], f"Expected error status code, got {response.status_code}"