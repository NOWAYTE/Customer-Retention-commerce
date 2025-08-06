# app/routes/api.py

from flask import Blueprint, request, jsonify, current_app
from ..models.churn import load_model, predict_churn
import pandas as pd
import os

api_bp = Blueprint('api', __name__)

# Load churn model once at import time
model = load_model()

# Compute absolute path to segments CSV
SEGMENTS_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '..',            # app/routes
        '..',            # app
        'data',          # data directory
        'customer_risk_segments.csv'
    )
)

@api_bp.route('/predict', methods=['POST'])
def predict():
    """
    POST JSON:
      {
        "Recency": ...,
        "Frequency": ...,
        "Monetary": ...,
        "TenureDays": ...,
        "AvgPurchaseGap": ...,
        "AvgBasketValue": ...,
        "BasketStdDev": ...,
        "UniqueProducts": ...
      }
    Returns:
      { "churn_prob": 0.42 }
    """
    data = request.get_json()
    prob = predict_churn(model, data)
    return jsonify({"churn_prob": prob})


@api_bp.route('/segments', methods=['GET'])
def segments():
    """
    Returns the full list of customer segments from CSV:
      [
        {"CustomerID": 12345, "Churn_Prob": 0.8, "Risk": "High"},
        ...
      ]
    """
    # Read CSV
    df = pd.read_csv(SEGMENTS_PATH)
    # Convert to list of dicts
    segments = df.to_dict(orient='records')
    return jsonify(segments)
