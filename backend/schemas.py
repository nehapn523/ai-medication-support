
from pydantic import BaseModel, Field, ConfigDict


# ==========================================
# PATIENT REGISTRATION INPUT
# ==========================================

class PatientInput(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)

    age: int = Field(..., ge=0, le=120)

    gender: str = Field(..., min_length=1)

    weight_kg: float = Field(..., gt=0, le=500)

    height_cm: float = Field(..., gt=0, le=300)

    chronic_conditions: str = "Unknown"

    drug_allergies: str = "Unknown"

    genetic_disorders: str = "Unknown"

    diagnosis: str = Field(..., min_length=1)

    symptoms: str = Field(..., min_length=1)

    model_config = ConfigDict(
        str_strip_whitespace=True
    )


# ==========================================
# MEDICATION ANALYSIS REQUEST
# ==========================================

class MedicationAnalysis(BaseModel):
    patient_id: int = Field(..., gt=0)


# ==========================================
# PATIENT REGISTRATION RESPONSE
# ==========================================

class PatientResponse(BaseModel):
    patient_id: int
    calculated_bmi: float


# ==========================================
# ANALYSIS RESPONSE
# ==========================================

class AnalysisResponse(BaseModel):
    patient_id: int

    calculated_bmi: float

    predicted_medication: str
    medication_confidence: float | None = None

    predicted_dosage_mg: float
    predicted_duration_days: float

    treatment_effectiveness: str
    effectiveness_confidence: float | None = None

    adverse_risk: str
    adverse_probability: float | None = None

    explanation: list[dict] = []

    explanation_note: str
    safety_note: str
