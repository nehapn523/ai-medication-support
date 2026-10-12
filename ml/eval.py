import pandas as pd
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)


# ==========================================
# PATHS
# ==========================================

ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = ROOT / "dataset" / "processed_medication.csv"

BACKEND = ROOT / "backend"


# ==========================================
# LOAD
# ==========================================

df = pd.read_csv(DATA_PATH)


# ==========================================
# FEATURES
# ==========================================

recommendation_features = [

    "Age",
    "Gender",
    "Weight_kg",
    "Height_cm",
    "BMI",
    "Chronic_Conditions",
    "Drug_Allergies",
    "Genetic_Disorders",
    "Diagnosis",
    "Symptoms",
    "Dosage_mg",
    "Duration_days"
]


analysis_features = [

    "Age",
    "Gender",
    "Weight_kg",
    "Height_cm",
    "BMI",
    "Chronic_Conditions",
    "Drug_Allergies",
    "Genetic_Disorders",
    "Diagnosis",
    "Symptoms",
    "Recommended_Medication",
    "Dosage_mg",
    "Duration_days"
]


# ==========================================
# LOAD MODELS
# ==========================================

medication_model = joblib.load(
    BACKEND / "medication_model.pkl"
)

medication_encoder = joblib.load(
    BACKEND / "medication_encoder.pkl"
)


effectiveness_model = joblib.load(
    BACKEND / "effectiveness_model.pkl"
)

effectiveness_encoder = joblib.load(
    BACKEND / "effectiveness_encoder.pkl"
)


adverse_model = joblib.load(
    BACKEND / "adverse_model.pkl"
)


# =====================================================
# MEDICATION
# =====================================================

med_df = df[
    df[
        "Recommended_Medication"
    ].notna()
].copy()


X_med = med_df[
    recommendation_features
]


y_med = medication_encoder.transform(
    med_df[
        "Recommended_Medication"
    ]
)


X_train, X_test, y_train, y_test = (

    train_test_split(

        X_med,

        y_med,

        test_size=0.2,

        random_state=42,

        stratify=y_med
    )
)


prediction = medication_model.predict(
    X_test
)


print("\n")
print("=" * 60)
print("MEDICATION RECOMMENDATION")
print("=" * 60)


print(
    "Accuracy:",
    round(
        accuracy_score(
            y_test,
            prediction
        ),
        4
    )
)


print(
    "Precision:",
    round(
        precision_score(
            y_test,
            prediction,
            average="weighted"
        ),
        4
    )
)


print(
    "Recall:",
    round(
        recall_score(
            y_test,
            prediction,
            average="weighted"
        ),
        4
    )
)


print(
    "F1:",
    round(
        f1_score(
            y_test,
            prediction,
            average="weighted"
        ),
        4
    )
)


print(
    "\nClassification Report:"
)

print(
    classification_report(
        y_test,
        prediction,
        target_names=
        medication_encoder.classes_
    )
)


# =====================================================
# EFFECTIVENESS
# =====================================================

X_eff = df[
    analysis_features
]


y_eff = effectiveness_encoder.transform(
    df[
        "Treatment_Effectiveness"
    ]
)


X_train, X_test, y_train, y_test = (

    train_test_split(

        X_eff,

        y_eff,

        test_size=0.2,

        random_state=42,

        stratify=y_eff
    )
)


prediction = effectiveness_model.predict(
    X_test
)


print("\n")
print("=" * 60)
print("TREATMENT EFFECTIVENESS")
print("=" * 60)


print(
    "Accuracy:",
    round(
        accuracy_score(
            y_test,
            prediction
        ),
        4
    )
)


print(
    "Precision:",
    round(
        precision_score(
            y_test,
            prediction,
            average="weighted",
            zero_division=0
        ),
        4
    )
)


print(
    "Recall:",
    round(
        recall_score(
            y_test,
            prediction,
            average="weighted",
            zero_division=0
        ),
        4
    )
)


print(
    "F1:",
    round(
        f1_score(
            y_test,
            prediction,
            average="weighted",
            zero_division=0
        ),
        4
    )
)


print(
    "\nClassification Report:"
)

print(
    classification_report(
        y_test,
        prediction,
        target_names=
        effectiveness_encoder.classes_,
        zero_division=0
    )
)


# =====================================================
# ADVERSE REACTION
# =====================================================

y_adv = df[
    "Adverse_Reactions"
].map({
    "No": 0,
    "Yes": 1
})


X_train, X_test, y_train, y_test = (

    train_test_split(

        X_eff,

        y_adv,

        test_size=0.2,

        random_state=42,

        stratify=y_adv
    )
)


prediction = adverse_model.predict(
    X_test
)


print("\n")
print("=" * 60)
print("ADVERSE REACTION")
print("=" * 60)


print(
    "Accuracy:",
    round(
        accuracy_score(
            y_test,
            prediction
        ),
        4
    )
)


print(
    "Precision:",
    round(
        precision_score(
            y_test,
            prediction,
            zero_division=0
        ),
        4
    )
)


print(
    "Recall:",
    round(
        recall_score(
            y_test,
            prediction,
            zero_division=0
        ),
        4
    )
)


print(
    "F1:",
    round(
        f1_score(
            y_test,
            prediction,
            zero_division=0
        ),
        4
    )
)


print(
    "\nClassification Report:"
)

print(
    classification_report(
        y_test,
        prediction,
        zero_division=0
    )
)


print(
    "\nConfusion Matrix:"
)

print(
    confusion_matrix(
        y_test,
        prediction
    )
)