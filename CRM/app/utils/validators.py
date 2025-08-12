"""
Input validation utilities for the CRM system.
"""
from datetime import datetime
from email_validator import validate_email, EmailNotValidError
from flask import jsonify
from functools import wraps

class ValidationError(Exception):
    """Custom exception for validation errors"""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        rv['code'] = self.status_code
        return rv

def validate_customer_data(data):
    """Validate customer data structure and content."""
    required_fields = {
        'customer_id': (str, "Customer ID is required"),
        'email': (str, "Valid email is required"),
        'recency': (int, "Recency (days since last purchase) is required"),
        'frequency': (int, "Purchase frequency is required"),
        'monetary': (float, "Monetary value is required")
    }
    
    # Check for missing fields
    missing_fields = [field for field, _ in required_fields.items() if field not in data]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
    
    # Validate field types
    for field, (field_type, error_msg) in required_fields.items():
        if not isinstance(data[field], field_type):
            try:
                data[field] = field_type(data[field])
            except (ValueError, TypeError):
                raise ValidationError(f"Invalid type for {field}: {error_msg}")
    
    # Validate email format
    try:
        validate_email(data['email'])
    except EmailNotValidError as e:
        raise ValidationError(f"Invalid email format: {str(e)}")
    
    # Validate numerical values
    if data['recency'] < 0:
        raise ValidationError("Recency cannot be negative")
    if data['frequency'] < 0:
        raise ValidationError("Frequency cannot be negative")
    if data['monetary'] < 0:
        raise ValidationError("Monetary value cannot be negative")
    
    return data

def handle_validation_error(f):
    ""
    Decorator to handle validation errors and return proper JSON responses.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return jsonify(e.to_dict()), e.status_code
        except Exception as e:
            return jsonify({
                'status': 'error',
                'message': 'An unexpected error occurred',
                'code': 500
            }), 500
    return decorated_function
