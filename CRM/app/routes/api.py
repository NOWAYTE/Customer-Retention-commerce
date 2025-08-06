# app/routes/api.py

from flask import Blueprint, request, jsonify
from ..models.churn import load_model, predict_churn
from ..models.segment import CustomerSegment
from ..extensions import db  # ensure you’ve imported this
# Remove pandas/os since we no longer read the CSV

api_bp = Blueprint('api', __name__)

# Load churn model once at import time
model = load_model()

@api_bp.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    prob = predict_churn(model, data)
    return jsonify({"churn_prob": prob})


@api_bp.route('/segments', methods=['GET'])
def segments():
    """
    Returns all customer segments from the database
    """
    segments = CustomerSegment.query.all()
    # Use the to_dict() method on each model instance
    return jsonify([seg.to_dict() for seg in segments])
