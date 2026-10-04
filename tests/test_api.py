import pytest
import secrets
from fastapi.testclient import TestClient
from main import app
from backend.predictor import predict_heart_disease

client = TestClient(app)

def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "2.0.0"

def test_model_prediction_direct():
    # Normal patient sample
    normal_patient = {
        "age": 35,
        "sex": 0,
        "cp": 2,
        "trestbps": 115,
        "chol": 170,
        "fbs": 0,
        "restecg": 0,
        "thalach": 175,
        "exang": 0,
        "oldpeak": 0.0,
        "slope": 2,
        "ca": 0,
        "thal": 0
    }
    risk, prob, level, factors, recs = predict_heart_disease(normal_patient)
    assert 0 <= risk <= 100
    assert 0.0 <= prob <= 1.0
    assert level in ["Low", "Moderate", "High"]
    assert len(factors) > 0
    assert len(recs) > 0

    # High risk patient sample
    high_risk_patient = {
        "age": 65,
        "sex": 1,
        "cp": 0,
        "trestbps": 160,
        "chol": 290,
        "fbs": 1,
        "restecg": 1,
        "thalach": 110,
        "exang": 1,
        "oldpeak": 3.0,
        "slope": 1,
        "ca": 2,
        "thal": 2
    }
    hr_risk, hr_prob, hr_level, hr_factors, hr_recs = predict_heart_disease(high_risk_patient)
    assert 0 <= hr_risk <= 100
    assert 0.0 <= hr_prob <= 1.0
    assert hr_level in ["Low", "Moderate", "High"]
    assert len(hr_factors) > 0
    assert len(hr_recs) > 0

def test_auth_registration_and_login():
    unique_user = f"testuser_{secrets.token_hex(4)}"
    password = "SuperSecretPassword123"

    # Register
    reg_res = client.post("/api/auth/register", json={
        "username": unique_user,
        "password": password,
        "full_name": "Test Physician"
    })
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["user"]["username"] == unique_user

    # Duplicate registration should fail
    dup_res = client.post("/api/auth/register", json={
        "username": unique_user,
        "password": password
    })
    assert dup_res.status_code == 400

    # Login with valid password
    login_res = client.post("/api/auth/login", json={
        "username": unique_user,
        "password": password
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]
    assert len(token) > 20

    # Login with invalid password
    bad_login = client.post("/api/auth/login", json={
        "username": unique_user,
        "password": "WrongPassword"
    })
    assert bad_login.status_code == 401

    # Verify Profile with Token
    profile_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert profile_res.status_code == 200
    assert profile_res.json()["username"] == unique_user

def test_prediction_api_and_history():
    unique_user = f"patient_{secrets.token_hex(4)}"
    password = "SafePassword99"
    reg = client.post("/api/auth/register", json={"username": unique_user, "password": password})
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Run prediction as authenticated user
    pred_res = client.post("/api/predict", json={
        "age": 55,
        "sex": 1,
        "cp": 1,
        "trestbps": 130,
        "chol": 220,
        "fbs": 0,
        "restecg": 0,
        "thalach": 160,
        "exang": 0,
        "oldpeak": 1.2,
        "slope": 1,
        "ca": 0,
        "thal": 2
    }, headers=headers)
    assert pred_res.status_code == 200
    pred_data = pred_res.json()
    assert "risk_score" in pred_data
    assert "risk_level" in pred_data
    assert "risk_factors" in pred_data
    assert "recommendations" in pred_data

    # Check history contains the record
    hist_res = client.get("/api/history", headers=headers)
    assert hist_res.status_code == 200
    items = hist_res.json()
    assert len(items) >= 1
    record_id = items[0]["id"]

    # Check user stats
    stats_res = client.get("/api/stats", headers=headers)
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_assessments"] >= 1
    assert stats["average_risk"] > 0

    # Delete the record
    del_res = client.delete(f"/api/history/{record_id}", headers=headers)
    assert del_res.status_code == 200

def test_live_sensors_api():
    res = client.get("/api/sensors/live")
    assert res.status_code == 200
    data = res.json()
    assert 50 <= data["pulse_bpm"] <= 120
    assert 50 <= data["heart_rate_bpm"] <= 120
    assert 90 <= data["spo2_percent"] <= 100
    assert 90 <= data["blood_pressure_systolic"] <= 160
    assert 60 <= data["blood_pressure_diastolic"] <= 100
