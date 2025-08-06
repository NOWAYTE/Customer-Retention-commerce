# tests/test_api.py

import json
from app.models.segment import CustomerSegment
from app.extensions import db

def test_predict_endpoint(client):
    payload = {
        "Recency": 30, "Frequency": 5, "Monetary": 200,
        "TenureDays": 100, "AvgPurchaseGap": 20,
        "AvgBasketValue": 40, "BasketStdDev": 5, "UniqueProducts": 5
    }
    resp = client.post("/api/predict",
                       json=payload)
    data = resp.get_json()
    assert resp.status_code == 200
    assert "churn_prob" in data
    assert 0.0 <= data["churn_prob"] <= 1.0

def test_segments_endpoint_empty(client):
    # No segments in DB yet → expect empty list
    resp = client.get("/api/segments")
    assert resp.status_code == 200
    assert resp.get_json() == []

def test_segments_endpoint_with_data(client, test_app):
    # Seed one segment
    with test_app.app_context():
        seg = CustomerSegment(
            customer_id=123,
            churn_prob=0.75,
            risk="High"
        )
        db.session.add(seg)
        db.session.commit()
    resp = client.get("/api/segments")
    data = resp.get_json()
    assert len(data) == 1
    assert data[0]["CustomerID"] == 123
    assert data[0]["Risk"] == "High"
