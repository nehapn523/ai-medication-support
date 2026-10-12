
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from database import create_tables, get_connection
from schemas import (
    PatientInput,
    MedicationAnalysis
)
from prediction import predict_all
from safety import check_safety


# ==========================================
# FASTAPI APPLICATION
# ==========================================

app = FastAPI(
    title="AI-Based Personalized Medication Support System",
    description=(
        "Academic demonstration of dataset-based medication "
        "and treatment outcome predictions."
    ),
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==========================================
# DATABASE INITIALIZATION
# ==========================================

@app.on_event("startup")
def startup_event():
    create_tables()


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():
    return {
        "message": "Medication Support API is running",
        "docs": "/docs"
    }


# ==========================================
# REGISTER PATIENT
# ==========================================

@app.post("/patients")
def register_patient(patient: PatientInput):
    data = patient.model_dump()

    height_m = data["height_cm"] / 100
    bmi = round(data["weight_kg"] / (height_m ** 2), 2)

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO patients (
                name,
                age,
                gender,
                weight_kg,
                height_cm,
                bmi,
                chronic_conditions,
                drug_allergies,
                genetic_disorders,
                diagnosis,
                symptoms
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["name"],
                data["age"],
                data["gender"],
                data["weight_kg"],
                data["height_cm"],
                bmi,
                data["chronic_conditions"],
                data["drug_allergies"],
                data["genetic_disorders"],
                data["diagnosis"],
                data["symptoms"]
            )
        )

        patient_id = cursor.lastrowid
        conn.commit()

        return {
            "message": "Patient registered successfully",
            "patient_id": patient_id,
            "calculated_bmi": bmi
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Patient registration failed: {str(exc)}"
        )

    finally:
        if "conn" in locals():
            conn.close()


# ==========================================
# GET PATIENT DETAILS
# ==========================================

@app.get("/patients/{patient_id}")
def get_patient(patient_id: int):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM patients WHERE id = ?",
            (patient_id,)
        )

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found."
            )

        return dict(row)

    finally:
        conn.close()


# ==========================================
# ANALYZE PATIENT
# ==========================================

@app.post("/analyze")
def analyze_patient(request: MedicationAnalysis):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM patients WHERE id = ?",
            (request.patient_id,)
        )

        row = cursor.fetchone()

        if row is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found. Register the patient first."
            )

        patient = dict(row)

        # Generate model predictions
        try:
            predictions = predict_all(patient)
        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Prediction failed: {str(exc)}"
            )

        # Check the limited configured allergy rules
        safety = check_safety(
            patient.get("drug_allergies", "Unknown"),
            predictions["predicted_medication"]
        )

        # A configured allergy alert takes precedence in the display.
        if safety["status"] == "HIGH ALERT":
            displayed_risk = "HIGH ALERT"
        else:
            displayed_risk = predictions["adverse_risk"]

        cursor.execute(
            """
            INSERT INTO analyses (
                patient_id,
                medication,
                dosage_mg,
                duration_days,
                predicted_medication,
                effectiveness,
                effectiveness_confidence,
                adverse_risk,
                adverse_probability
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                request.patient_id,
                predictions["predicted_medication"],
                predictions["predicted_dosage_mg"],
                predictions["predicted_duration_days"],
                predictions["predicted_medication"],
                predictions["treatment_effectiveness"],
                predictions["effectiveness_confidence"],
                displayed_risk,
                predictions["adverse_probability"]
            )
        )

        conn.commit()

        return {
            "message": "Analysis completed",
            "patient_id": request.patient_id,
            **predictions,
            "adverse_risk": displayed_risk,
            "safety_check": safety
        }

    except HTTPException:
        raise

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(exc)}"
        )

    finally:
        conn.close()


# ==========================================
# PATIENT ANALYSIS HISTORY
# ==========================================

@app.get("/history/{patient_id}")
def get_history(patient_id: int):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id FROM patients WHERE id = ?",
            (patient_id,)
        )

        if cursor.fetchone() is None:
            raise HTTPException(
                status_code=404,
                detail="Patient not found."
            )

        cursor.execute(
            """
            SELECT *
            FROM analyses
            WHERE patient_id = ?
            ORDER BY created_at DESC
            """,
            (patient_id,)
        )

        rows = cursor.fetchall()

        return {
            "patient_id": patient_id,
            "total_analyses": len(rows),
            "history": [dict(row) for row in rows]
        }

    finally:
        conn.close()
