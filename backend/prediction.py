
import joblib
import pandas as pd

from pathlib import Path


# ==========================================
# LOAD TRAINED MODELS
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

medication_model = joblib.load(
    BASE_DIR / "medication_model.pkl"
)
medication_encoder = joblib.load(
    BASE_DIR / "medication_encoder.pkl"
)

dosage_model = joblib.load(
    BASE_DIR / "dosage_model.pkl"
)
duration_model = joblib.load(
    BASE_DIR / "duration_model.pkl"
)

effectiveness_model = joblib.load(
    BASE_DIR / "effectiveness_model.pkl"
)
effectiveness_encoder = joblib.load(
    BASE_DIR / "effectiveness_encoder.pkl"
)

adverse_model = joblib.load(
    BASE_DIR / "adverse_model.pkl"
)


# ==========================================
# HELPER FUNCTIONS
# ==========================================

def get_confidence(model, data):
    """Return the predicted class probability, when available."""
    try:
        probabilities = model.predict_proba(data)[0]
        return round(float(max(probabilities)) * 100, 2)
    except (AttributeError, ValueError):
        return None


def get_adverse_probability(model, data):
    """Return the probability of the adverse-reaction class (1)."""
    try:
        probabilities = model.predict_proba(data)[0]
        classes = list(model.named_steps["classifier"].classes_)

        if 1 in classes:
            index = classes.index(1)
            return round(float(probabilities[index]) * 100, 2)

        return 0.0
    except (AttributeError, ValueError, KeyError):
        return None


def get_feature_explanation(model, data):
    """Return the five most important model features."""
    try:
        preprocessor = model.named_steps["preprocessor"]
        classifier = model.named_steps["classifier"]

        feature_names = preprocessor.get_feature_names_out()
        importances = classifier.feature_importances_

        ranked = sorted(
            zip(feature_names, importances),
            key=lambda item: item[1],
            reverse=True
        )[:5]

        return [
            {
                "feature": str(name),
                "importance": round(float(score), 4)
            }
            for name, score in ranked
        ]

    except (AttributeError, ValueError, KeyError):
        return []


# ==========================================
# MAIN PREDICTION FUNCTION
# ==========================================

def predict_all(patient):
    """
    Generate experimental dataset-based predictions.

    These outputs are for an academic demonstration only.
    They must not be used to prescribe or change treatment.
    """

    age = float(patient["age"])
    weight = float(patient["weight_kg"])
    height_cm = float(patient["height_cm"])

    if weight <= 0 or height_cm <= 0:
        raise ValueError("Weight and height must be positive.")

    if not 0 <= age <= 120:
        raise ValueError("Age must be between 0 and 120.")

    height_m = height_cm / 100
    bmi = round(weight / (height_m ** 2), 2)

    # --------------------------------------
    # 1. PREPARE PATIENT FEATURES
    # --------------------------------------

    patient_data = {
        "Age": age,
        "Gender": patient["gender"],
        "Weight_kg": weight,
        "Height_cm": height_cm,
        "BMI": bmi,
        "Chronic_Conditions": patient.get(
            "chronic_conditions", "Unknown"
        ),
        "Drug_Allergies": patient.get(
            "drug_allergies", "Unknown"
        ),
        "Genetic_Disorders": patient.get(
            "genetic_disorders", "Unknown"
        ),
        "Diagnosis": patient["diagnosis"],
        "Symptoms": patient["symptoms"]
    }

    medication_data = pd.DataFrame([patient_data])

    # --------------------------------------
    # 2. PREDICT MEDICATION
    # --------------------------------------

    medication_class = medication_model.predict(
        medication_data
    )[0]

    medication_name = medication_encoder.inverse_transform(
        [int(medication_class)]
    )[0]

    medication_confidence = get_confidence(
        medication_model, medication_data
    )

    # --------------------------------------
    # 3. PREPARE TREATMENT FEATURES
    # --------------------------------------

    treatment_data = pd.DataFrame([{
        **patient_data,
        "Recommended_Medication": medication_name
    }])

    # --------------------------------------
    # 4. PREDICT DOSAGE
    # --------------------------------------

    dosage_prediction = float(
        dosage_model.predict(treatment_data)[0]
    )

    # Round only for display; this is NOT a validated dose.
    dosage_prediction = round(max(0.0, dosage_prediction), 2)

    # --------------------------------------
    # 5. PREDICT DURATION
    # --------------------------------------

    duration_prediction = float(
        duration_model.predict(treatment_data)[0]
    )

    duration_prediction = round(
        max(0.0, duration_prediction), 2
    )

    # --------------------------------------
    # 6. PREPARE ANALYSIS FEATURES
    # --------------------------------------

    analysis_data = pd.DataFrame([{
        **patient_data,
        "Recommended_Medication": medication_name,
        "Dosage_mg": dosage_prediction,
        "Duration_days": duration_prediction
    }])

    # --------------------------------------
    # 7. PREDICT TREATMENT EFFECTIVENESS
    # --------------------------------------

    effectiveness_class = effectiveness_model.predict(
        analysis_data
    )[0]

    effectiveness_label = effectiveness_encoder.inverse_transform(
        [int(effectiveness_class)]
    )[0]

    effectiveness_confidence = get_confidence(
        effectiveness_model, analysis_data
    )

    # --------------------------------------
    # 8. PREDICT ADVERSE-REACTION RISK
    # --------------------------------------

    adverse_class = int(
        adverse_model.predict(analysis_data)[0]
    )

    adverse_probability = get_adverse_probability(
        adverse_model, analysis_data
    )

    if adverse_class == 1:
        adverse_risk = "HIGH"
    else:
        adverse_risk = "LOW"

    # --------------------------------------
    # 9. RETURN ALL RESULTS
    # --------------------------------------

    return {
        "calculated_bmi": bmi,

        "predicted_medication": str(medication_name),
        "medication_confidence": medication_confidence,

        "predicted_dosage_mg": dosage_prediction,
        "predicted_duration_days": duration_prediction,

        "treatment_effectiveness": str(effectiveness_label),
        "effectiveness_confidence": effectiveness_confidence,

        "adverse_risk": adverse_risk,
        "adverse_probability": adverse_probability,

        "explanation": get_feature_explanation(
            medication_model, medication_data
        ),

        "explanation_note": (
            "Feature importance describes model behaviour; "
            "it does not establish medical causation."
        ),

        "safety_note": (
            "All predictions are experimental estimates from "
            "the supplied dataset, not medical advice or "
            "validated prescriptions. A qualified healthcare "
            "professional must determine medication, dose, "
            "duration, and treatment suitability."
        )
    }
