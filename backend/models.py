from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any

class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Unique username")
    password: str = Field(..., min_length=4, max_length=100, description="Password")
    full_name: Optional[str] = Field(default="", max_length=100)

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    full_name: Optional[str] = ""
    created_at: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class PredictionInput(BaseModel):
    age: int = Field(default=52, ge=18, le=120, description="Age in years")
    sex: int = Field(default=1, ge=0, le=1, description="Gender (0: Female, 1: Male)")
    cp: int = Field(default=1, ge=0, le=3, description="Chest pain type (0: Typical, 1: Atypical, 2: Non-anginal, 3: Asymptomatic)")
    trestbps: int = Field(default=125, ge=70, le=250, description="Resting blood pressure in mm Hg")
    chol: int = Field(default=212, ge=80, le=600, description="Serum cholesterol in mg/dl")
    fbs: int = Field(default=0, ge=0, le=1, description="Fasting blood sugar > 120 mg/dl (0: No, 1: Yes)")
    restecg: int = Field(default=0, ge=0, le=2, description="Resting ECG results (0: Normal, 1: ST-T wave abnormality, 2: LV hypertrophy)")
    thalach: int = Field(default=168, ge=50, le=250, description="Maximum heart rate achieved")
    exang: int = Field(default=0, ge=0, le=1, description="Exercise induced angina (0: No, 1: Yes)")
    oldpeak: float = Field(default=1.0, ge=0.0, le=10.0, description="ST depression induced by exercise relative to rest")
    slope: int = Field(default=2, ge=0, le=2, description="Slope of the peak exercise ST segment (0: Upsloping, 1: Flat, 2: Downsloping)")
    ca: int = Field(default=0, ge=0, le=4, description="Number of major vessels colored by flourosopy (0-4)")
    thal: int = Field(default=2, ge=0, le=3, description="Thalassemia (0: Normal, 1: Fixed defect, 2: Reversible defect, 3: Unknown)")

class RiskFactor(BaseModel):
    feature: str
    label: str
    value: Any
    severity: str  # "normal", "moderate", "high"
    message: str

class Recommendation(BaseModel):
    category: str  # "Cardiovascular Care", "Dietary Strategy", "Physical Activity", "Lifestyle & Monitoring"
    title: str
    description: str
    priority: str  # "High", "Medium", "Routine"

class PredictionOutput(BaseModel):
    risk_score: int
    risk_probability: float
    risk_level: str  # "Low", "Moderate", "High"
    assessment_id: Optional[int] = None
    timestamp: str
    risk_factors: List[RiskFactor]
    recommendations: List[Recommendation]
    input_summary: Dict[str, Any]

class HistoryItem(BaseModel):
    id: int
    username: str
    risk: int
    risk_level: str
    timestamp: str
    details: Optional[Dict[str, Any]] = None

class StatsResponse(BaseModel):
    total_assessments: int
    average_risk: float
    last_risk: Optional[int] = None
    last_assessment: Optional[str] = None
    distribution: Dict[str, int]

class LiveSensors(BaseModel):
    pulse_bpm: int
    heart_rate_bpm: int
    spo2_percent: int
    blood_pressure_systolic: int
    blood_pressure_diastolic: int
    status: str
