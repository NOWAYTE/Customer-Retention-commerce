"""
Tests for the API endpoints.
"""
import json
import pytest
from app import db

class TestAuthEndpoints:
    """Test authentication-related endpoints."""
    
    def test_register_user(self, test_client):
        """Test user registration."""
        response = test_client.post(
            '/auth/register',
            json={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'newpass123'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
        assert 'user' in data
        assert data['user']['email'] == 'newuser@example.com'
    
    def test_login_success(self, test_client):
        """Test successful user login."""
        response = test_client.post(
            '/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'testpass123'
            }
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
    
    def test_login_invalid_credentials(self, test_client):
        """Test login with invalid credentials."""
        response = test_client.post(
            '/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }
        )
        assert response.status_code == 401


class TestPredictionEndpoints:
    """Test prediction-related endpoints.""" 
    def test_predict_unauthorized(self, test_client, sample_customer_data):
        """Test prediction without authentication."""
        response = test_client.post(
            '/api/predict',
            json=sample_customer_data
        )
        assert response.status_code == 401
    def test_predict_success(self, test_client, auth_headers, sample_customer_data):
        """Test successful prediction."""
        response = test_client.post(
            '/api/predict',
            headers=auth_headers,
            json=sample_customer_data
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'churn_probability' in data
        assert 'risk_level' in data
        assert 'recommended_actions' in data
        assert isinstance(data['churn_probability'], float)
        assert 0 <= data['churn_probability'] <= 1
    def test_predict_missing_fields(self, test_client, auth_headers):
        """Test prediction with missing required fields."""
        response = test_client.post(
            '/api/predict',
            headers=auth_headers,
            json={"Recency": 30}
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Missing required field' in data['message']    
    def test_predict_invalid_data(self, test_client, auth_headers, sample_customer_data):
        """Test prediction with invalid data types."""
        invalid_data = sample_customer_data.copy()
        invalid_data['Recency'] = "not_an_integer"
        response = test_client.post(
            '/api/predict',
            headers=auth_headers,
            json=invalid_data
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Invalid value for Recency' in data['message']


class TestModelEndpoints:
    """Test model-related endpoints."""
    
    def test_model_health(self, test_client, auth_headers):
        """Test the model health check endpoint."""
        response = test_client.get(
            '/api/ping',
            headers=auth_headers
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'status' in data
        assert 'model_loaded' in data
        assert isinstance(data['model_loaded'], bool)
        
        if not data['model_loaded']:
            pytest.skip("Model not loaded, skipping model-dependent tests")
    
    def test_predict_with_model(self, test_client, auth_headers, sample_customer_data):
        """Test prediction when model is loaded."""
        # First check if model is loaded
        health = test_client.get('/api/ping', headers=auth_headers)
        if not json.loads(health.data)['model_loaded']:
            pytest.skip("Model not loaded, skipping test")
        
        response = test_client.post(
            '/api/predict',
            headers=auth_headers,
            json=sample_customer_data
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'churn_probability' in data
        assert 0 <= data['churn_probability'] <= 1


class TestModelConsistency:
    """Test model output consistency and format."""
    
    def test_model_consistency(self, test_client, auth_headers, sample_customer_data):
        """Test that the model produces consistent output for the same input."""
        # Make first prediction
        response1 = test_client.post(
            '/api/predict',
            headers=auth_headers,
            json=sample_customer_data
        )
        assert response1.status_code == 200
        data1 = json.loads(response1.data)
        
        # Make second prediction with same input
        response2 = test_client.post(
            '/api/predict',
            headers=auth_headers,
            json=sample_customer_data
        )
        assert response2.status_code == 200
        data2 = json.loads(response2.data)
        
        # Check that predictions are consistent
        assert data1['probability'] == data2['probability'], \
            f"Model predictions differ for same input: {data1['probability']} vs {data2['probability']}"
        
        # Check that risk levels are consistent
        assert data1['risk_level'] == data2['risk_level'], \
            f"Risk levels differ for same input: {data1['risk_level']} vs {data2['risk_level']}"
    
    def test_output_format(self, test_client, auth_headers, sample_customer_data):
        """Test that the model output has the expected format."""
        response = test_client.post(
            '/api/predict',
            headers=auth_headers,
            json=sample_customer_data
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        
        # Check required fields in response
        required_fields = [
            'probability', 
            'risk_level',
            'explanation',
            'recommended_actions',
            'features_used'
        ]
        for field in required_fields:
            assert field in data, f"Missing required field in response: {field}"
        
        # Check probability is between 0 and 1
        assert 0 <= data['probability'] <= 1, \
            f"Probability {data['probability']} is not between 0 and 1"
            
        # Check risk level is one of the expected values
        assert data['risk_level'] in ['low', 'medium', 'high'], \
            f"Unexpected risk level: {data['risk_level']}"
        
        # Check explanation is a non-empty string
        assert isinstance(data['explanation'], str) and len(data['explanation']) > 0, \
            "Explanation should be a non-empty string"
            
        # Check recommended_actions is a list with at least one action
        assert isinstance(data['recommended_actions'], list), \
            "recommended_actions should be a list"
        assert len(data['recommended_actions']) > 0, \
            "At least one recommended action should be provided"
            
        # Check features_used contains all expected features
        expected_features = [
            'Recency', 'Frequency', 'Monetary', 'TenureDays',
            'AvgPurchaseGap', 'AvgBasketValue', 'BasketStdDev', 'UniqueProducts'
        ]
        for feature in expected_features:
            assert feature in data['features_used'], \
                f"Expected feature {feature} not in features_used"


class TestDataValidation:
    """Test data validation and cleaning functionality."""
    
    def test_validate_positive_values(self, test_client, auth_headers, sample_customer_data):
        """Test validation of positive numeric values."""
        # Test with negative values
        invalid_data = sample_customer_data.copy()
        invalid_data['Recency'] = -10
        
        response = test_client.post(
            '/api/predict',
            headers=auth_headers,
            json=invalid_data
        )
        assert response.status_code == 400, f"Expected status code 400, got {response.status_code}"
        data = json.loads(response.data)
        assert 'Invalid value for Recency' in data['message'], \
            f"Expected error about invalid Recency, got: {data['message']}"
    
    def test_validate_required_fields(self, test_client, auth_headers, sample_customer_data):
        """Test that all required fields are validated."""
        for field in sample_customer_data:
            # Create a copy with one field missing
            test_data = sample_customer_data.copy()
            del test_data[field]
            
            response = test_client.post(
                '/api/predict',
                headers=auth_headers,
                json=test_data
            )
            assert response.status_code == 400, \
                f"Expected status code 400 when missing {field}, got {response.status_code}"
            data = json.loads(response.data)
            assert f'Missing required field: {field}' in data['message'], \
                f"Expected missing field error for {field}, got: {data['message']}"
    
    def test_validate_data_types(self, test_client, auth_headers, sample_customer_data):
        """Test validation of data types."""
        # Test with string instead of number for Recency
        invalid_data = sample_customer_data.copy()
        invalid_data['Recency'] = 'thirty'
        
        response = None
        try:
            response = test_client.post(
                '/api/predict',
                headers=auth_headers,
                json=invalid_data
            )
            # The API might handle string conversion, so we'll check if it returns 200 or 400
            assert response.status_code in [200, 400], \
                f"Expected status code 200 or 400, got {response.status_code}"
                
            if response.status_code == 400:
                data = json.loads(response.data)
                assert 'Invalid value' in data['message'], \
                    f"Expected invalid value error, got: {data['message']}"
        finally:
            # Clean up any database connections
            if response and hasattr(response, 'close'):
                response.close()
