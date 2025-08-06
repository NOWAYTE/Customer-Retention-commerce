# app/routes/api.py

from flask import Blueprint, request, jsonify
from ..models.churn import load_model, predict_churn

api_bp = Blueprint('api', __name__)

# Load model at import time
model = load_model()

@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    Expects JSON: { "Recency": ..., "Frequency": ..., ... }
    Returns: { "churn_prob": 0.42 }
    """
    data = request.get_json()
    prob = predict_churn(model, data)
    return jsonify({"churn_prob": prob})

@api_bp.route('/segments', methods=['GET'])
def segments():
    # Later: read from DB or CSV
    # Example stub:
    sample = [
        {"CustomerID": 12345, "churn_prob": 0.8, "risk": "High"},
        {"CustomerID": 23456, "churn_prob": 0.2, "risk": "Low"}
    ]
    return jsonify(sample)
