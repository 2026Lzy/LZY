import sys
sys.path.append(".")
from fastapi.testclient import TestClient
from backend.app import app

client = TestClient(app)
test_features = [0.1]*14

def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "运行正常"

def test_fault_api():
    response = client.post("/api/fault/predict", json={"features": test_features, "unit": 1})
    assert response.status_code == 200
    data = response.json()
    assert "fault_label" in data
    assert "confidence" in data

def test_rul_api():
    response = client.post("/api/rul/predict", json={"features": test_features, "unit": 1})
    assert response.status_code == 200
    data = response.json()
    assert "rul_value" in data
    assert "risk_level" in data

def test_maintenance_api():
    response = client.post("/api/maintenance/optimize", json={
        "unit": 1, "fault_label": 1, "fault_confidence": 0.85, "rul": 30, "device_weight": 0.5
    })
    assert response.status_code == 200
    data = response.json()
    assert "priority" in data
    assert "suggestion" in data

