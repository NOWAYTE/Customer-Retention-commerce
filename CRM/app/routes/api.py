"""
API routes for customer retention predictions.
"""
import sys
import os
from flask import Blueprint, request, jsonify, current_app
import joblib
from datetime import datetime

print("\n=== Loading API routes module ===", file=sys.stderr)

# Create the blueprint
api_bp = Blueprint('api', __name__)
print(f"✓ Created API blueprint: {api_bp}", file=sys.stderr)

# Try to load the model with error handling
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'churn_model.pkl')
model = None

try:
    print(f"Looking for model at: {os.path.abspath(MODEL_PATH)}", file=sys.stderr)
    if os.path.exists(MODEL_PATH):
        print("Model file exists, loading...", file=sys.stderr)
        model = joblib.load(MODEL_PATH)
        print("✓ Model loaded successfully", file=sys.stderr)
    else:
        print(f"✗ Model file not found at {MODEL_PATH}", file=sys.stderr)
        # Try alternative path for development
        alt_path = os.path.join(os.path.dirname(__file__), '..', 'models', 'churn_model.pkl')
        print(f"Trying alternative path: {os.path.abspath(alt_path)}", file=sys.stderr)
        if os.path.exists(alt_path):
            model = joblib.load(alt_path)
            print("✓ Model loaded from alternative path", file=sys.stderr)
        else:
            print(f"✗ Model not found at alternative path either", file=sys.stderr)
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
    """
    Predict customer churn probability.
    
    Expected JSON payload:
    {
        "customer_id": "string",
        "email": "string",
        "recency": int,
        "frequency": int,
        "monetary": float
    }
    """
    # Check if model is loaded
    if model is None:
        return jsonify({
            'status': 'error',
            'message': 'Prediction model not available',
            'model_loaded': False
        }), 503
        
    try:
        # Validate input data
        data = request.get_json()
        if not data:
            raise Exception("No data provided")
            
        # Validate and clean input data
        validated_data = {
            'customer_id': data.get('customer_id'),
            'email': data.get('email'),
            'recency': data.get('recency'),
            'frequency': data.get('frequency'),
            'monetary': data.get('monetary')
        }
        
        # Prepare features for prediction
        features = [
            validated_data['recency'],
            validated_data['frequency'],
            validated_data['monetary']
        ]
        
        # Make prediction
        try:
            probability = model.predict_proba([features])[0][1]
        except Exception as e:
            current_app.logger.error(f"Prediction error: {str(e)}")
            raise Exception(f"Error making prediction: {str(e)}", 500)
        
        # Generate response
        response = {
            'status': 'success',
            'customer_id': validated_data['customer_id'],
            'churn_probability': float(probability),
            'risk_level': 'high' if probability > 0.5 else 'moderate' if probability > 0.3 else 'low',
            'explanation': 'Test explanation',
            'recommended_actions': ['Test action 1', 'Test action 2'],
            'timestamp': datetime.utcnow().isoformat(),
            'model_loaded': True
        }
        
        # Log the prediction
        current_app.logger.info(
            f"Prediction for customer {validated_data['customer_id']}: "
            f"probability={probability:.2f}, risk={response['risk_level']}"
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Unexpected error in prediction: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'model_loaded': model is not None
        }), 500

print("✓ API routes initialized", file=sys.stderr)
