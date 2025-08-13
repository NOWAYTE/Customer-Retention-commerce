"""
Test configuration and fixtures for the CRM application.
"""
import os
import tempfile
import pytest
from app import create_app, db
from app.models.user import User  # Import the User model

# Test configuration
class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test-secret-key'
    WTF_CSRF_ENABLED = False
    MARKETING_WEBHOOK_ENABLED = False  # Disable webhooks by default in tests

@pytest.fixture(scope='module')
def test_app():
    """Create and configure a new app instance for each test module."""
    # Create a temporary file to isolate the database for each test module
    db_fd, db_path = tempfile.mkstemp()
    
    app = create_app(TestConfig)
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    
    # Create the database and load test data
    with app.app_context():
        db.create_all()
    
    yield app  # Testing happens here
    
    # Clean up the database file after tests complete
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture(scope='function')
def test_client(test_app, init_database):
    """Create a test client for the Flask application."""
    with test_app.test_client() as testing_client:
        with test_app.app_context():
            yield testing_client
            # Clean up the session after each test
            db.session.remove()
            db.get_engine(test_app).dispose()

@pytest.fixture(scope='function')
def init_database(test_app):
    """Initialize the database with test data."""
    with test_app.app_context():
        db.create_all()
        
        # Create a test user
        user = User(
            username='testuser',
            email='test@example.com',
            password='testpass'  # Will be hashed by the User model
        )
        db.session.add(user)
        db.session.commit()
        
        yield db  # This is where testing happens
        
        # Clean up after tests
        db.session.remove()
        db.drop_all()
        db.get_engine(test_app).dispose()

@pytest.fixture
def auth_headers(test_client, init_database):
    """Get authentication headers for API requests."""
    # Log in the test user
    login_response = test_client.post(
        '/auth/login',
        json={
            'email': 'test@example.com',
            'password': 'testpass'
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
