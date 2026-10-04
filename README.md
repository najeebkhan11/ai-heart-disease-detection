# 🫀 CardioAI — Clinical AI Heart Disease Screening & Detection Platform

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Scikit-Learn](https://img.shields.io/badge/scikit--learn-1.4%2B-F7931E?logo=scikit-learn&logoColor=white)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![GitHub Repository](https://img.shields.io/badge/GitHub-najeebkhan11%2Fai--heart--disease--detection-181717?logo=github)](https://github.com/najeebkhan11/ai-heart-disease-detection)

**CardioAI** is a full-stack, enterprise-grade cardiovascular risk screening and decision-support web platform. Utilizing a Random Forest machine learning model trained on the UCI Heart Disease dataset, it translates 13 key clinical and hemodynamic biomarkers into calibrated risk probabilities, clinical factor attributions, real-time simulated telemetry, and exportable patient reports.

---

## 🌟 Key Features

- **🧠 Machine Learning Risk Engine**:
  - Calibrated probability prediction classifying cardiac risk into **Low (≤30%)**, **Moderate (31–50%)**, and **High (>50%)**.
  - Feature-level clinical attribution highlighting which biomarkers (e.g. resting BP, serum cholesterol, exercise angina, ST depression) contribute most heavily.
- **⚡ Decoupled High-Performance FastAPI Backend**:
  - RESTful API endpoints for authentication, model inference, telemetry simulation, and patient history.
  - Interactive OpenAPI / Swagger UI live at `/docs`.
  - Secure **JWT Bearer Token** authentication with **PBKDF2-HMAC-SHA256** password hashing.
  - Thread-safe SQLite database with automated schema migration.
- **🎨 Modern Cardiology Glassmorphism Frontend**:
  - Intuitive clinical calculators organized into Demographics, Hemodynamics, ECG Stress Testing, and Fluoroscopy.
  - Real-time animated **Lead II Electrocardiogram (ECG) monitor** rendered on HTML5 Canvas.
  - Dynamic SVG semi-circle risk gauge with animated probability counter.
  - Preset fast-fill patient profiles (*Normal Patient*, *High-Risk Patient*).
  - Categorized clinical recommendations (Cardiovascular Care, Dietary Strategy, Exercise Prescription, Monitoring).
  - **Print / PDF Medical Summary Export**: Formatted clinical laboratory report for patient records.
- **📜 Patient History & Trends**:
  - Individual record management with deletion and complete history clearance.
  - Longitudinal statistics (total screenings, average risk index, latest diagnosis status).

---

## 🏗️ System Architecture

```
heart_disease_app/
├── backend/
│   ├── __init__.py
│   ├── auth.py              # JWT authentication & PBKDF2 password hashing
│   ├── database.py          # SQLite connection & schema migration
│   ├── models.py            # Pydantic schemas for auth, prediction, history
│   ├── predictor.py         # ML model loader, inference & clinical risk logic
│   └── routes/
│       ├── __init__.py
│       ├── auth_routes.py   # /api/auth/register, /api/auth/login, /api/auth/me
│       ├── predict_routes.py# /api/predict, /api/stats
│       ├── history_routes.py# /api/history (CRUD operations)
│       └── sensor_routes.py # /api/sensors/live (telemetry simulation)
├── frontend/
│   ├── index.html           # Modern Single-Page Application (SPA)
│   ├── css/
│   │   └── styles.css       # Glassmorphism, cardiology dark/light theme
│   └── js/
│       ├── api.js           # API client with token storage
│       ├── ecg.js           # Real-time animated canvas ECG monitor
│       └── app.js           # Form controllers, gauge animations, report export
├── tests/
│   ├── __init__.py
│   └── test_api.py          # Pytest unit & integration test suite
├── heart_model.pkl          # Trained Random Forest Classifier
├── heart.csv                # UCI Heart Disease dataset
├── Heart.ipynb              # Model exploratory data analysis & training notebook
├── main.py                  # FastAPI application entrypoint & static mount
├── run.py                   # One-click startup launcher
├── requirements.txt         # Production dependencies
└── README.md                # Documentation
```

---

## 🔬 Clinical Parameters Analyzed

| Parameter | Medical Label | Physiological Range | Description |
| :--- | :--- | :--- | :--- |
| **age** | Patient Age | 18–100 yrs | Biological age |
| **sex** | Gender | 0: Female, 1: Male | Biological sex |
| **cp** | Chest Pain Type | 0–3 | Typical angina, Atypical, Non-anginal, Asymptomatic |
| **trestbps** | Resting Blood Pressure | 80–200 mm Hg | Resting systolic blood pressure on admission |
| **chol** | Serum Cholesterol | 100–450 mg/dl | Serum cholesterol level |
| **fbs** | Fasting Blood Sugar | 0: No, 1: Yes | FBS > 120 mg/dl (indicator of diabetic metabolic strain) |
| **restecg** | Resting ECG Results | 0–2 | 0: Normal, 1: ST-T wave abnormality, 2: LV hypertrophy |
| **thalach** | Max Heart Rate | 70–220 bpm | Maximum heart rate achieved during exercise stress test |
| **exang** | Exercise Angina | 0: No, 1: Yes | Exercise-induced transient angina pectoris |
| **oldpeak** | ST Depression | 0.0–6.0 mm | ST depression induced by exercise relative to rest |
| **slope** | ST Segment Slope | 0–2 | Upsloping, Flat, Downsloping peak exercise slope |
| **ca** | Fluoroscopy Vessels | 0–4 | Number of major vessels colored by fluoroscopy |
| **thal** | Thallium Scintigraphy | 0–3 | Normal, Fixed defect, Reversible defect |

---

## 🚀 Quickstart & Installation

### 1. Prerequisites
- Python 3.10 or higher
- Git

### 2. Clone the Repository
```bash
git clone https://github.com/najeebkhan11/ai-heart-disease-detection.git
cd ai-heart-disease-detection
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the Application
Start the unified full-stack application with a single command:
```bash
python run.py
```
*The web browser will automatically open to `http://localhost:8000`.*

### 5. Access Interactive API Documentation
Navigate to `http://localhost:8000/docs` to test all REST endpoints interactively via Swagger UI.

---

## 🧪 Running Automated Tests

Run the comprehensive Pytest suite:
```bash
python -m pytest tests/test_api.py -v
```

All 5 test suites (System Health, Model Inference, JWT Authentication, Prediction History, and Live Telemetry) will execute.

---

## 📡 REST API Reference

| Method | Endpoint | Description | Auth Required |
| :--- | :--- | :--- | :---: |
| `GET` | `/api/health` | Health check & service metadata | No |
| `POST` | `/api/auth/register` | Register new user account | No |
| `POST` | `/api/auth/login` | Authenticate user & return JWT token | No |
| `GET` | `/api/auth/me` | Fetch authenticated user profile | **Yes** |
| `POST` | `/api/predict` | Run AI model risk inference & analysis | Optional |
| `GET` | `/api/stats` | Retrieve aggregate patient statistics | **Yes** |
| `GET` | `/api/history` | List authenticated user assessment history | **Yes** |
| `DELETE` | `/api/history/{id}` | Delete a specific prediction record | **Yes** |
| `DELETE` | `/api/history` | Clear complete prediction history | **Yes** |
| `GET` | `/api/sensors/live` | Simulated real-time cardiac vitals telemetry | No |

---

## ⚠️ Medical Disclaimer

This project is developed for **educational, demonstration, and research screening purposes only**. It does not constitute formal medical diagnosis, clinical treatment advice, or prescriptive cardiology care. Always consult a board-certified physician or cardiologist for evaluation of cardiovascular symptoms.
