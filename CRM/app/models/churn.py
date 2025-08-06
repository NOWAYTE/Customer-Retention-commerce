# app/models/churn.py

import joblib
import numpy as np
import os

MODEL_PATH = os.path.join(
    os.path.dirname(__file__),
    '../../data/churn_model.pkl'  # adjust path if placed elsewhere
)

_feature_order = [
    'Recency','Frequency','Monetary',
    'TenureDays','AvgPurchaseGap',
    'AvgBasketValue','BasketStdDev','UniqueProducts'
]

def load_model():
    """Load and return the trained churn model."""
    return joblib.load(MODEL_PATH)

def predict_churn(model, data_dict):
    """
    Given a dict of feature values, returns churn probability.
    """
    # Ensure correct order
    X = np.array([[data_dict.get(f, 0) for f in _feature_order]])
    prob = model.predict_proba(X)[0, 1]
    return float(prob)
