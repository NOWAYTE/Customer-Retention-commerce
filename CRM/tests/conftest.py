"""
Test configuration and fixtures for the CRM application.
"""
import os
import tempfile
import pytest
from app import create_app, db
from app.models import get_model
from werkzeug.security import generate_password_hash

# Test configuration
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    MARKETING_WEBHOOK_ENABLED = False  # Disable webhooks by default in tests

@pytest.fixture(scope='module')
def test_client():
    """Create a test client for the Flask application."""
    app = create_app(TestConfig)
    testing_client = app.test_client()
    
    # Establish an application context before running the tests
    ctx = app.app_context()
    ctx.push()
    
    yield testing_client
    
    ctx.pop()

@pytest.fixture(scope='module')
def init_database():
    """Initialize the test database."""
    # Create the database and the database table
    db.create_all()
    
    # Insert test user
    User = get_model('User')
    user = User(
        username='testuser',
        email='test@example.com',
        password_hash=generate_password_hash('testpass123')
    )
    db.session.add(user)
    db.session.commit()
    
    yield db  # this is where the testing happens
    
    db.session.remove()
    db.drop_all()

@pytest.fixture
def auth_headers(test_client, init_database):
    """Get authentication headers for API requests."""
    # Log in the test user
    login_response = test_client.post(
        '/auth/login',
        json={
            'email': 'test@example.com',
            'password': 'testpass123'
        }
    )
    token = login_response.get_json().get('access_token')
    return {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

@pytest.fixture
def sample_customer_data():
    """Return sample customer data for testing predictions."""
    return {
        "Recency": 30,
        "Frequency": 5,
        "Monetary": 99.99,
        "TenureDays": 180,
        "AvgPurchaseGap": 14.5,
        "AvgBasketValue": 49.99,
        "BasketStdDev": 10.2,
        "UniqueProducts": 12
    }
