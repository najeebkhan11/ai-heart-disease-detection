import random
from fastapi import APIRouter
from backend.models import LiveSensors

router = APIRouter(prefix="/api/sensors", tags=["Sensors Telemetry"])

@router.get("/live", response_model=LiveSensors)
def get_live_sensors():
    pulse = random.randint(68, 86)
    hr = pulse + random.randint(-2, 2)
    spo2 = random.randint(96, 99)
    systolic = random.randint(114, 126)
    diastolic = random.randint(72, 82)
    
    return {
        "pulse_bpm": pulse,
        "heart_rate_bpm": hr,
        "spo2_percent": spo2,
        "blood_pressure_systolic": systolic,
        "blood_pressure_diastolic": diastolic,
        "status": "Normal Sinus Rhythm"
    }
