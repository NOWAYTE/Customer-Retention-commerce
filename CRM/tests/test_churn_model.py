# tests/test_churn_model.py
import pytest
from app.models.churn import load_model, predict_churn

@pytest.fixture(scope="module")
def model():
    return load_model()

def test_predict_churn_low_risk(model):
    low_risk = {
        "Recency": 10, "Frequency": 20, "Monetary": 500,
        "TenureDays": 100, "AvgPurchaseGap": 5,
        "AvgBasketValue": 25, "BasketStdDev": 3, "UniqueProducts": 10
    }
    prob = predict_churn(model, low_risk)
    assert 0.0 <= prob < 0.5

def test_predict_churn_high_risk(model):
    high_risk = {
        "Recency": 200, "Frequency": 1, "Monetary": 5,
        "TenureDays": 200, "AvgPurchaseGap": 200,
        "AvgBasketValue": 5, "BasketStdDev": 0, "UniqueProducts": 1
    }
    prob = predict_churn(model, high_risk)
    assert 0.5 < prob <= 1.0
