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
except Exception as e:
    print(f"✗ Error loading prediction model: {str(e)}", file=sys.stderr)
    model = None

# Required fields for prediction
REQUIRED_FEATURES = [
    'Recency', 'Frequency', 'Monetary',
    'TenureDays', 'AvgPurchaseGap',
    'AvgBasketValue', 'BasketStdDev', 'UniqueProducts'
]

def validate_customer_data(data):
    """Validate and clean customer data for prediction"""
    if not data:
        raise ValueError("No data provided")
        
    validated = {}
    
    # Check for required fields
    for field in REQUIRED_FEATURES:
        if field not in data:
            raise ValueError(f"Missing required field: {field}")
        
        # Convert to appropriate type
        try:
            if field in ['Recency', 'Frequency', 'TenureDays', 'UniqueProducts']:
                validated[field] = int(data[field])
            else:  # Monetary, AvgPurchaseGap, AvgBasketValue, BasketStdDev
                validated[field] = float(data[field])
                
            # Additional validation
            if validated[field] < 0:
                raise ValueError(f"{field} cannot be negative")
                
        except (ValueError, TypeError) as e:
            raise ValueError(f"Invalid value for {field}: {data[field]}")
    
    return validated

def get_risk_explanation(prob, data):
    """Generate explanation for the risk score"""
    risk_level = "high" if prob > 0.5 else "moderate" if prob > 0.3 else "low"
    
    # Generate explanation based on key factors
    factors = []
    if data['Recency'] > 100:
        factors.append(f"high recency ({data['Recency']} days since last purchase)")
    if data['Frequency'] < 2:
        factors.append(f"low purchase frequency ({data['Frequency']} purchases)")
    if data['Monetary'] < 10:
        factors.append(f"low monetary value (${data['Monetary']:.2f})")
    if data['AvgPurchaseGap'] > 30:
        factors.append(f"long average time between purchases ({data['AvgPurchaseGap']:.1f} days)")
    
    explanation = f"Customer has {risk_level} risk of churning"
    if factors:
        explanation += " due to: " + ", ".join(factors) + "."
    else:
        explanation += "."
    
    return explanation

def get_recommended_actions(prob, data):
    """Generate recommended actions based on risk level"""
    if prob > 0.7:
        return [
            "Send personalized retention offer",
            "Assign to account manager for personal outreach",
            "Provide exclusive discount"
        ]
    elif prob > 0.4:
        return [
            "Send targeted email campaign",
            "Offer loyalty points bonus"
        ]
    else:
        return ["Standard retention campaign"]

@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    Predict customer churn probability.
    
    Expected JSON payload:
    {
        "Recency": int,
        "Frequency": int,
        "Monetary": float,
        "TenureDays": int,
        "AvgPurchaseGap": float,
        "AvgBasketValue": float,
        "BasketStdDev": float,
        "UniqueProducts": int
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
        # Get and validate input data
        data = request.get_json()
        validated_data = validate_customer_data(data)
        
        # Prepare features in the correct order expected by the model
        features = [
            validated_data['Recency'],
            validated_data['Frequency'],
            validated_data['Monetary'],
            validated_data['TenureDays'],
            validated_data['AvgPurchaseGap'],
            validated_data['AvgBasketValue'],
            validated_data['BasketStdDev'],
            validated_data['UniqueProducts']
        ]
        
        # Make prediction
        try:
            probability = model.predict_proba([features])[0][1]
        except Exception as e:
            current_app.logger.error(f"Prediction error: {str(e)}")
            raise ValueError(f"Error making prediction: {str(e)}")
        
        # Generate response
        response = {
            'status': 'success',
            'churn_probability': float(probability),
            'risk_level': 'high' if probability > 0.5 else 'moderate' if probability > 0.3 else 'low',
            'explanation': get_risk_explanation(probability, validated_data),
            'recommended_actions': get_recommended_actions(probability, validated_data),
            'timestamp': datetime.utcnow().isoformat(),
            'model_loaded': True,
            'features_used': validated_data
        }
        
        # Log the prediction
        current_app.logger.info(
            f"Prediction completed - "
            f"Probability: {probability:.2f}, "
            f"Risk: {response['risk_level']}"
        )
        
        return jsonify(response), 200
        
    except ValueError as ve:
        return jsonify({
            'status': 'error',
            'message': str(ve),
            'model_loaded': model is not None
        }), 400
    except Exception as e:
        current_app.logger.error(f"Unexpected error in prediction: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': 'An unexpected error occurred',
            'model_loaded': model is not None
        }), 500

# Simple health check endpoint
@api_bp.route('/ping', methods=['GET'])
def ping():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'API is working',
        'model_loaded': model is not None,
        'timestamp': datetime.utcnow().isoformat()
    }), 200

print("✓ API routes initialized", file=sys.stderr)
