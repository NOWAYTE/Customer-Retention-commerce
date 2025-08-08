# app/routes/api.py

from flask import Blueprint, request, jsonify, current_app
from ..models.churn import load_model, predict_churn
from ..models.segment import CustomerSegment
from ..extensions import db
from datetime import datetime

api_bp = Blueprint('api', __name__)

# Required fields for prediction
REQUIRED_FIELDS = [
    'Recency', 'Frequency', 'Monetary',
    'TenureDays', 'AvgPurchaseGap',
    'AvgBasketValue', 'BasketStdDev', 'UniqueProducts'
]

# Load churn model once at import time
model = load_model()

def validate_input(data):
    """Validate input data and return error message if invalid"""
    if not data:
        return "No data provided"
    
    missing_fields = [field for field in REQUIRED_FIELDS if field not in data]
    if missing_fields:
        return f"Missing required fields: {', '.join(missing_fields)}"
    
    try:
        # Convert all values to float to ensure they're numbers
        for field in REQUIRED_FIELDS:
            float(data[field])
    except (ValueError, TypeError):
        return f"Invalid data type for one or more fields. All fields must be numbers."
    
    return None

def get_risk_explanation(prob, data):
    """Generate explanation for the risk score"""
    risk_level = "high" if prob > 0.5 else "moderate" if prob > 0.3 else "low"
    
    # Simple explanation based on key factors
    factors = []
    if data['Recency'] > 100:
        factors.append(f"high recency ({data['Recency']} days)")
    if data['Frequency'] < 2:
        factors.append(f"low purchase frequency ({data['Frequency']})")
    if data['Monetary'] < 10:
        factors.append(f"low monetary value (${data['Monetary']})")
    
    explanation = f"Customer has {risk_level} churn risk."
    if factors:
        explanation += " Key factors: " + ", ".join(factors) + "."
    
    return explanation

def trigger_marketing_action(customer_id, risk_score):
    """Trigger appropriate marketing action based on risk score"""
    if risk_score > 0.7:
        return "immediate_retention_campaign"
    elif risk_score > 0.4:
        return "targeted_offer"
    return "standard_engagement"

@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    Predict churn probability for a customer
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          required: [Recency, Frequency, Monetary, TenureDays, AvgPurchaseGap, AvgBasketValue, BasketStdDev, UniqueProducts]
          properties:
            customer_id:
              type: string
              description: Unique customer identifier
            Recency: {type: number}
            Frequency: {type: number}
            Monetary: {type: number}
            TenureDays: {type: number}
            AvgPurchaseGap: {type: number}
            AvgBasketValue: {type: number}
            BasketStdDev: {type: number}
            UniqueProducts: {type: number}
    responses:
      200:
        description: Churn prediction result
        schema:
          type: object
          properties:
            customer_id: {type: string}
            churn_probability: {type: number}
            risk_level: {type: string}
            explanation: {type: string}
            marketing_action: {type: string}
            timestamp: {type: string}
    """
    data = request.get_json()
    
    # Validate input
    error = validate_input(data)
    if error:
        return jsonify({"error": error}), 400
    
    try:
        # Get prediction
        prob = predict_churn(model, data)
        
        # Prepare response
        response = {
            "customer_id": data.get('customer_id', 'unknown'),
            "churn_probability": prob,
            "risk_level": "high" if prob > 0.5 else "moderate" if prob > 0.3 else "low",
            "explanation": get_risk_explanation(prob, data),
            "marketing_action": trigger_marketing_action(data.get('customer_id'), prob),
            "timestamp": datetime.utcnow().isoformat()
        }
        
        return jsonify(response)
        
    except Exception as e:
        current_app.logger.error(f"Prediction error: {str(e)}")
        return jsonify({"error": "Failed to process prediction"}), 500

@api_bp.route('/segments', methods=['GET'])
def segments():
    """
    Returns all customer segments from the database
    """
    segments = CustomerSegment.query.all()
    # Use the to_dict() method on each model instance
    return jsonify([seg.to_dict() for seg in segments])

