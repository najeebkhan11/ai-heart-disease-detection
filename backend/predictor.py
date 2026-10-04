import os
from pathlib import Path
from typing import Dict, Any, List, Tuple
import joblib
import numpy as np

MODEL_PATH = Path(__file__).resolve().parent.parent / "heart_model.pkl"

_model = None

def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Trained model not found at {MODEL_PATH}")
        _model = joblib.load(str(MODEL_PATH))
    return _model

def analyze_risk_factors(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    factors = []
    
    # Blood Pressure (trestbps)
    bp = data.get("trestbps", 120)
    if bp >= 140:
        factors.append({
            "feature": "trestbps",
            "label": "Resting Blood Pressure",
            "value": f"{bp} mm Hg",
            "severity": "high",
            "message": "Hypertension Stage 2 detected. Elevated arterial pressure increases strain on cardiac muscle."
        })
    elif bp >= 130:
        factors.append({
            "feature": "trestbps",
            "label": "Resting Blood Pressure",
            "value": f"{bp} mm Hg",
            "severity": "moderate",
            "message": "Pre-hypertension / Stage 1. Mildly elevated vascular resistance."
        })
    else:
        factors.append({
            "feature": "trestbps",
            "label": "Resting Blood Pressure",
            "value": f"{bp} mm Hg",
            "severity": "normal",
            "message": "Resting blood pressure within optimal clinical range."
        })

    # Cholesterol (chol)
    chol = data.get("chol", 200)
    if chol >= 240:
        factors.append({
            "feature": "chol",
            "label": "Serum Cholesterol",
            "value": f"{chol} mg/dl",
            "severity": "high",
            "message": "Hypercholesterolemia. High LDL and plaque buildup risk in coronary arteries."
        })
    elif chol >= 200:
        factors.append({
            "feature": "chol",
            "label": "Serum Cholesterol",
            "value": f"{chol} mg/dl",
            "severity": "moderate",
            "message": "Borderline high cholesterol level. Dietary lipid management advised."
        })
    else:
        factors.append({
            "feature": "chol",
            "label": "Serum Cholesterol",
            "value": f"{chol} mg/dl",
            "severity": "normal",
            "message": "Serum lipid concentration within healthy physiological bounds."
        })

    # Exercise Induced Angina (exang)
    exang = data.get("exang", 0)
    if exang == 1:
        factors.append({
            "feature": "exang",
            "label": "Exercise Angina",
            "value": "Present",
            "severity": "high",
            "message": "Exertional ischemia indicated: transient chest pain or discomfort triggered by physical effort."
        })
    else:
        factors.append({
            "feature": "exang",
            "label": "Exercise Angina",
            "value": "Absent",
            "severity": "normal",
            "message": "No exercise-induced ischemic chest discomfort reported."
        })

    # ST Depression (oldpeak)
    oldpeak = data.get("oldpeak", 0.0)
    if oldpeak >= 2.0:
        factors.append({
            "feature": "oldpeak",
            "label": "ST Depression (oldpeak)",
            "value": f"{oldpeak} mm",
            "severity": "high",
            "message": "Significant electrocardiographic ST segment depression during stress test. High myocardial ischemia risk."
        })
    elif oldpeak >= 1.0:
        factors.append({
            "feature": "oldpeak",
            "label": "ST Depression (oldpeak)",
            "value": f"{oldpeak} mm",
            "severity": "moderate",
            "message": "Moderate ST segment depression noted under exertion."
        })
    else:
        factors.append({
            "feature": "oldpeak",
            "label": "ST Depression (oldpeak)",
            "value": f"{oldpeak} mm",
            "severity": "normal",
            "message": "Minimal or normal ST segment deviation observed."
        })

    # Major Vessels Blocked (ca)
    ca = data.get("ca", 0)
    if ca >= 1:
        factors.append({
            "feature": "ca",
            "label": "Fluoroscopy Vessels (ca)",
            "value": f"{ca} vessels",
            "severity": "high",
            "message": f"{ca} major vessel(s) showed fluoroscopic contrast attenuation, suggesting possible coronary narrowing."
        })
    else:
        factors.append({
            "feature": "ca",
            "label": "Fluoroscopy Vessels (ca)",
            "value": "0 vessels",
            "severity": "normal",
            "message": "No major coronary vessel calcification/blockage observed on fluoroscopy."
        })

    # Maximum Heart Rate (thalach)
    thalach = data.get("thalach", 150)
    age = data.get("age", 50)
    expected_max = 220 - age
    if thalach < (expected_max * 0.7):
        factors.append({
            "feature": "thalach",
            "label": "Max Heart Rate Achieved",
            "value": f"{thalach} bpm",
            "severity": "moderate",
            "message": f"Peak heart rate is lower than expected chronotropic capacity (~{int(expected_max)} bpm)."
        })
    else:
        factors.append({
            "feature": "thalach",
            "label": "Max Heart Rate Achieved",
            "value": f"{thalach} bpm",
            "severity": "normal",
            "message": "Appropriate chronotropic response during maximum exertion."
        })

    # Fasting Blood Sugar (fbs)
    fbs = data.get("fbs", 0)
    if fbs == 1:
        factors.append({
            "feature": "fbs",
            "label": "Fasting Blood Sugar",
            "value": "> 120 mg/dl",
            "severity": "moderate",
            "message": "Elevated fasting blood glucose. Diabetes and metabolic syndrome elevate endothelial risk."
        })

    return factors

def generate_recommendations(risk_level: str, factors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    recs = []
    
    if risk_level == "High":
        recs.append({
            "category": "Cardiovascular Care",
            "title": "Comprehensive Cardiologist Consultation",
            "description": "Schedule a specialized clinical cardiovascular evaluation, including a resting 12-lead ECG, echocardiogram, or coronary CT angiography.",
            "priority": "High"
        })
        recs.append({
            "category": "Dietary Strategy",
            "title": "Therapeutic Lifestyle Changes (TLC) Diet",
            "description": "Adopt strict dietary sodium restriction (< 1,500 mg/day) and eliminate trans-fats, focusing on soluble fiber to lower serum LDL.",
            "priority": "High"
        })
        recs.append({
            "category": "Physical Activity",
            "title": "Medically Supervised Exercise Plan",
            "description": "Avoid strenuous, unmonitored anaerobic bursts. Consult your physician for a prescribed, cardiac-safe progressive walking regimen.",
            "priority": "High"
        })
        recs.append({
            "category": "Lifestyle & Monitoring",
            "title": "Daily Blood Pressure & Pulse Telemetry",
            "description": "Log morning and evening resting blood pressure and resting pulse. Keep a symptom journal for exertional dyspnea or angina.",
            "priority": "High"
        })
    elif risk_level == "Moderate":
        recs.append({
            "category": "Cardiovascular Care",
            "title": "Primary Care Physician Review",
            "description": "Review fasting lipid panels, HbA1c, and resting hemodynamics with your primary doctor within 3-4 weeks.",
            "priority": "Medium"
        })
        recs.append({
            "category": "Dietary Strategy",
            "title": "Mediterranean Dietary Pattern",
            "description": "Incorporate extra-virgin olive oil, omega-3 rich fish, leafy greens, walnuts, and complex grains to protect endothelial function.",
            "priority": "Medium"
        })
        recs.append({
            "category": "Physical Activity",
            "title": "Aerobic Conditioning",
            "description": "Target 150 minutes of moderate aerobic activity weekly (e.g. brisk walking, swimming, light cycling) split across 5 sessions.",
            "priority": "Medium"
        })
        recs.append({
            "category": "Lifestyle & Monitoring",
            "title": "Stress & Sleep Hygiene Optimization",
            "description": "Ensure 7-8 hours of restorative sleep and introduce mindfulness or breathing exercises to regulate autonomic sympathetic tone.",
            "priority": "Medium"
        })
    else:
        recs.append({
            "category": "Cardiovascular Care",
            "title": "Routine Preventive Checkups",
            "description": "Maintain regular annual health screenings, lipid profiles, and blood pressure checks to monitor baseline cardiovascular metrics.",
            "priority": "Routine"
        })
        recs.append({
            "category": "Dietary Strategy",
            "title": "Heart-Healthy Balanced Nutrition",
            "description": "Continue a wholesome, nutrient-dense diet rich in antioxidants, whole fruits, lean proteins, and plenty of water.",
            "priority": "Routine"
        })
        recs.append({
            "category": "Physical Activity",
            "title": "Active Lifestyle Maintenance",
            "description": "Sustain regular cardio and functional strength exercises at least 3-4 times weekly to support optimal metabolic reserve.",
            "priority": "Routine"
        })
        recs.append({
            "category": "Lifestyle & Monitoring",
            "title": "Proactive Health Tracking",
            "description": "Periodically re-evaluate your vitals and risk profile. Keep tobacco-free and limit excess alcohol intake.",
            "priority": "Routine"
        })
        
    return recs

def predict_heart_disease(data: Dict[str, Any]) -> Tuple[int, float, str, List[Dict[str, Any]], List[Dict[str, Any]]]:
    model = get_model()
    
    # 13 features matching model training order:
    # age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
    feature_vector = np.array([[
        float(data.get("age", 50)),
        float(data.get("sex", 1)),
        float(data.get("cp", 0)),
        float(data.get("trestbps", 120)),
        float(data.get("chol", 200)),
        float(data.get("fbs", 0)),
        float(data.get("restecg", 0)),
        float(data.get("thalach", 150)),
        float(data.get("exang", 0)),
        float(data.get("oldpeak", 0.0)),
        float(data.get("slope", 1)),
        float(data.get("ca", 0)),
        float(data.get("thal", 2)),
    ]])
    
    # Get probability for class 1 (heart disease risk)
    prob_class1 = float(model.predict_proba(feature_vector)[0][1])
    risk_score = int(round(prob_class1 * 100))
    
    if risk_score <= 30:
        risk_level = "Low"
    elif risk_score <= 50:
        risk_level = "Moderate"
    else:
        risk_level = "High"
        
    risk_factors = analyze_risk_factors(data)
    recommendations = generate_recommendations(risk_level, risk_factors)
    
    return risk_score, prob_class1, risk_level, risk_factors, recommendations
