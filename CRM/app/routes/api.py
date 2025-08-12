"""
API routes for customer retention predictions - Minimal version
"""
import sys
from flask import Blueprint, jsonify, current_app

print("\n=== Loading MINIMAL API routes module ===", file=sys.stderr)

# Create the blueprint
api_bp = Blueprint('api', __name__)
print(f"✓ Created minimal API blueprint: {api_bp}", file=sys.stderr)

# Simple test route
@api_bp.route('/ping')
def ping():
    print("Ping route called", file=sys.stderr)
    return jsonify({
        'status': 'success',
        'message': 'pong',
        'blueprint': api_bp.name,
        'endpoint': 'ping'
    })

# Simple predict route without model loading
@api_bp.route('/predict', methods=['POST'])
def predict():
    """Minimal predict endpoint for testing"""
    print("Minimal predict route called", file=sys.stderr)
    try:
        # Just return a mock response for now
        return jsonify({
            'status': 'success',
            'message': 'Prediction successful (minimal version)',
            'blueprint': api_bp.name,
            'endpoint': 'predict',
            'data': {
                'churn_probability': 0.25,
                'risk_level': 'low',
                'explanation': 'Minimal test response - model not loaded',
                'recommended_actions': ['Test action 1', 'Test action 2']
            }
        })
    except Exception as e:
        print(f"Error in minimal predict route: {str(e)}", file=sys.stderr)
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

print("✓ Added minimal routes to API blueprint", file=sys.stderr)

# Note: We'll gradually add back the full functionality once this works
