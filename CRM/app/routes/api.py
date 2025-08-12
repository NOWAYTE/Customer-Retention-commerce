"""
API routes for customer retention predictions.
"""
from flask import Blueprint, request, jsonify, current_app
import joblib
import os
from datetime import datetime
from ..utils.validators import validate_customer_data, handle_validation_error, ValidationError
from ..models import get_model
from ..extensions import db

api_bp = Blueprint('api', __name__)

# Load the model when the module is imported
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'churn_model.pkl')
try:
    model = joblib.load(MODEL_PATH)
    current_app.logger.info("Successfully loaded the prediction model")
except Exception as e:
    current_app.logger.error(f"Error loading prediction model: {str(e)}")
    model = None

# Required fields for prediction
REQUIRED_FIELDS = ['recency', 'frequency', 'monetary']

def get_risk_explanation(prob, data):
    """Generate explanation for the risk score"""
    risk_level = "high" if prob > 0.5 else "moderate" if prob > 0.3 else "low"
    
    # Generate explanation based on key factors
    factors = []
    if data['recency'] > 100:
        factors.append(f"high recency ({data['recency']} days since last purchase)")
    if data['frequency'] < 2:
        factors.append(f"low purchase frequency ({data['frequency']} purchases)")
    if data['monetary'] < 10:
        factors.append(f"low monetary value (${data['monetary']:.2f})")
    
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
@handle_validation_error
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
    try:
        # Validate input data
        data = request.get_json()
        if not data:
            raise ValidationError("No data provided")
            
        # Validate and clean input data
        validated_data = validate_customer_data(data)
        
        # Prepare features for prediction
        features = [
            validated_data['recency'],
            validated_data['frequency'],
            validated_data['monetary']
        ]
        
        # Make prediction
        if model is None:
            raise ValidationError("Prediction model not available", status_code=503)
            
        probability = model.predict_proba([features])[0][1]
        
        # Generate response
        response = {
            'status': 'success',
            'customer_id': validated_data['customer_id'],
            'churn_probability': float(probability),
            'risk_level': 'high' if probability > 0.5 else 'moderate' if probability > 0.3 else 'low',
            'explanation': get_risk_explanation(probability, validated_data),
            'recommended_actions': get_recommended_actions(probability, validated_data),
            'timestamp': datetime.utcnow().isoformat()
        }
        
        # Log the prediction
        current_app.logger.info(
            f"Prediction for customer {validated_data['customer_id']}: "
            f"probability={probability:.2f}, risk={response['risk_level']}"
        )
        
        return jsonify(response), 200
        
    except Exception as e:
        current_app.logger.error(f"Error in prediction: {str(e)}")
        raise ValidationError(str(e), status_code=500)

@api_bp.route('/segments', methods=['GET'])
@handle_validation_error
def get_segments():
    """Get all customer segments"""
    try:
        Segment = get_model('CustomerSegment')
        segments = Segment.query.all()
        return jsonify({
            'status': 'success',
            'segments': [segment.to_dict() for segment in segments]
        }), 200
    except Exception as e:
        current_app.logger.error(f"Error fetching segments: {str(e)}")
        raise ValidationError("Failed to fetch segments", status_code=500)
