"""
API routes for customer retention predictions
"""
import sys
import os
from flask import Blueprint, jsonify, request, current_app
import joblib
from datetime import datetime

print("\n=== Loading API routes module ===", file=sys.stderr)

# Create the blueprint
api_bp = Blueprint('api', __name__)
print(f"✓ Created API blueprint: {api_bp}", file=sys.stderr)

# Try to load the model with error handling
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'churn_model.pkl')
model = None

try:
    print(f"Looking for model at: {os.path.abspath(MODEL_PATH)}", file=sys.stderr)
    if os.path.exists(MODEL_PATH):
        print("Model file exists, loading...", file=sys.stderr)
        model = joblib.load(MODEL_PATH)
        print("✓ Model loaded successfully", file=sys.stderr)
    else:
        print(f"✗ Model file not found at {MODEL_PATH}", file=sys.stderr)
except Exception as e:
    print(f"✗ Error loading prediction model: {str(e)}", file=sys.stderr)
    model = None

# Simple test route
@api_bp.route('/ping')
def ping():
    """Test endpoint to verify API is working"""
    print("Ping route called", file=sys.stderr)
    return jsonify({
        'status': 'success',
        'message': 'pong',
        'blueprint': api_bp.name,
        'endpoint': 'ping',
        'model_loaded': model is not None
    })

# Simple predict route with model check
@api_bp.route('/predict', methods=['POST'])
def predict():
    """Minimal predict endpoint with model check"""
    print("Predict route called", file=sys.stderr)
    
    if model is None:
        return jsonify({
            'status': 'error',
            'message': 'Prediction model not available',
            'model_loaded': False
        }), 503
    
    try:
        # Just return a mock response for now
        return jsonify({
            'status': 'success',
            'message': 'Prediction successful (model loaded)',
            'blueprint': api_bp.name,
            'endpoint': 'predict',
            'model_loaded': True,
            'data': {
                'churn_probability': 0.25,
                'risk_level': 'low',
                'explanation': 'Test response - model loaded but using mock data',
                'recommended_actions': ['Test action 1', 'Test action 2']
            }
        })
    except Exception as e:
        print(f"Error in predict route: {str(e)}", file=sys.stderr)
        return jsonify({
            'status': 'error',
            'message': str(e),
            'model_loaded': model is not None
        }), 500

print("✓ API routes initialized", file=sys.stderr)
