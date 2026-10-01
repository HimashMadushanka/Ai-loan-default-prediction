import pytest
from fastapi.testclient import TestClient
from api.main import app, API_KEY


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True


def test_model_info_requires_auth(client):
    # Without header
    res_no_key = client.get("/model/info")
    assert res_no_key.status_code == 401

    # With invalid header
    res_bad_key = client.get("/model/info", headers={"X-API-Key": "wrong-key"})
    assert res_bad_key.status_code == 403

    # With valid header
    res_valid = client.get("/model/info", headers={"X-API-Key": API_KEY})
    assert res_valid.status_code == 200
    data = res_valid.json()
    assert "model_version" in data
    assert "features" in data


def test_predict_endpoint_valid_payload(client):
    payload = {
        "age": 29,
        "income": 65000.0,
        "employment_years": 5.0,
        "home_ownership": "MORTGAGE",
        "loan_amount": 15000.0,
        "loan_purpose": "PERSONAL",
        "credit_history_years": 7.0,
    }
    response = client.post("/predict", json=payload, headers={"X-API-Key": API_KEY})
    assert response.status_code == 200
    data = response.json()
    assert "result" in data
    assert "explanation" in data
    assert "log_id" in data
    assert data["result"]["prediction"] in ["Default", "Non-Default"]
    assert 0.0 <= data["result"]["default_probability"] <= 1.0


def test_predict_endpoint_invalid_payload(client):
    payload = {
        "age": 12,  # Invalid age < 18
        "income": -500.0,  # Invalid negative income
        "employment_years": 0.0,
        "home_ownership": "UNKNOWN",
        "loan_amount": 1000.0,
        "loan_purpose": "PERSONAL",
        "credit_history_years": 1.0,
    }
    response = client.post("/predict", json=payload, headers={"X-API-Key": API_KEY})
    assert response.status_code in [422, 400]
