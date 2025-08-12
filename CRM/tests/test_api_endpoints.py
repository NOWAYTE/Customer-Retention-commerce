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
            json={"Recency": 30}  # Missing other required fields
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'message' in data
        assert 'Missing required field' in data['message']
    
    def test_predict_invalid_data(self, test_client, auth_headers, sample_customer_data):
        """Test prediction with invalid data types."""
        invalid_data = sample_customer_data.copy()
        invalid_data['Recency'] = "not_an_integer"  # Invalid type
        
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
