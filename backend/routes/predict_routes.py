import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from backend.models import PredictionInput, PredictionOutput, StatsResponse
from backend.predictor import predict_heart_disease
from backend.database import get_db
from backend.auth import get_optional_user, get_current_user

router = APIRouter(prefix="/api", tags=["Prediction & Analytics"])

@router.post("/predict", response_model=PredictionOutput)
def run_prediction(input_data: PredictionInput, current_user: Optional[dict] = Depends(get_optional_user)):
    data_dict = input_data.model_dump()
    risk_score, prob, risk_level, risk_factors, recommendations = predict_heart_disease(data_dict)
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    assessment_id = None
    
    # Save to history if user is authenticated
    if current_user and "username" in current_user:
        username = current_user["username"]
        details_json = json.dumps({
            "inputs": data_dict,
            "risk_score": risk_score,
            "probability": prob,
            "risk_level": risk_level
        })
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO history (username, risk, risk_level, details, timestamp) VALUES (?, ?, ?, ?, ?)",
                (username, risk_score, risk_level, details_json, timestamp)
            )
            assessment_id = cursor.lastrowid

    return {
        "risk_score": risk_score,
        "risk_probability": round(prob, 4),
        "risk_level": risk_level,
        "assessment_id": assessment_id,
        "timestamp": timestamp,
        "risk_factors": risk_factors,
        "recommendations": recommendations,
        "input_summary": data_dict
    }

@router.get("/stats", response_model=StatsResponse)
def get_user_stats(current_user: dict = Depends(get_current_user)):
    username = current_user["username"]
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT risk, risk_level, timestamp FROM history WHERE username = ? ORDER BY id DESC", (username,))
        rows = cursor.fetchall()
        
    total = len(rows)
    if total == 0:
        return {
            "total_assessments": 0,
            "average_risk": 0.0,
            "last_risk": None,
            "last_assessment": None,
            "distribution": {"Low": 0, "Moderate": 0, "High": 0}
        }
        
    risks = [r["risk"] for r in rows]
    avg_risk = round(sum(risks) / total, 1)
    last_risk = rows[0]["risk"]
    last_ts = rows[0]["timestamp"]
    
    dist = {"Low": 0, "Moderate": 0, "High": 0}
    for r in rows:
        lvl = r["risk_level"] or ("Low" if r["risk"] <= 30 else ("Moderate" if r["risk"] <= 50 else "High"))
        if lvl in dist:
            dist[lvl] += 1
        else:
            dist[lvl] = 1

    return {
        "total_assessments": total,
        "average_risk": avg_risk,
        "last_risk": last_risk,
        "last_assessment": last_ts,
        "distribution": dist
    }
