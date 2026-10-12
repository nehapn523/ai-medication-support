
import joblib
import pandas as pd

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.metrics import accuracy_score, mean_absolute_error


# ==========================================
# PATHS
# ==========================================

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "dataset" / "processed_medication.csv"
BACKEND_PATH = ROOT / "backend"
BACKEND_PATH.mkdir(parents=True, exist_ok=True)

df = pd.read_csv(DATA_PATH)

# ==========================================
# DATA CLEANING
# ==========================================

required = [
    "Age", "Gender", "Weight_kg", "Height_cm",
    "Chronic_Conditions", "Drug_Allergies",
    "Genetic_Disorders", "Diagnosis", "Symptoms",
    "Recommended_Medication", "Dosage_mg", "Duration_days",
    "Treatment_Effectiveness", "Adverse_Reactions"
]

missing = set(required) - set(df.columns)
if missing:
    raise ValueError(f"Missing dataset columns: {sorted(missing)}")

# Calculate BMI from height and weight
height = pd.to_numeric(df["Height_cm"], errors="coerce") / 100
weight = pd.to_numeric(df["Weight_kg"], errors="coerce")

df["BMI"] = weight / height.pow(2)
df.loc[(height <= 0) | (weight <= 0), "BMI"] = float("nan")

# Normalize numeric fields
for col in ["Age", "Weight_kg", "Height_cm", "BMI",
            "Dosage_mg", "Duration_days"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# ==========================================
# FEATURES
# ==========================================

base_numeric = ["Age", "Weight_kg", "Height_cm", "BMI"]

base_categorical = [
    "Gender", "Chronic_Conditions", "Drug_Allergies",
    "Genetic_Disorders", "Diagnosis", "Symptoms"
]

# Medicine is predicted from patient details only.
medication_features = base_numeric + base_categorical

# Dosage and duration are learned from patient details
# and the medicine label in historical dataset records.
treatment_features = (
    base_numeric
    + base_categorical
    + ["Recommended_Medication"]
)

def make_preprocessor(numeric_cols, categorical_cols):
    numeric_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_pipeline = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("encoder", OneHotEncoder(handle_unknown="ignore"))
    ])

    return ColumnTransformer([
        ("numeric", numeric_pipeline, numeric_cols),
        ("categorical", categorical_pipeline, categorical_cols)
    ])


med_preprocessor = make_preprocessor(
    base_numeric, base_categorical
)

treatment_preprocessor = make_preprocessor(
    base_numeric,
    base_categorical + ["Recommended_Medication"]
)


def classifier_pipeline(preprocessor):
    return Pipeline([
        ("preprocessor", preprocessor),
        ("classifier", RandomForestClassifier(
            n_estimators=300,
            class_weight="balanced",
            random_state=42,
            n_jobs=-1
        ))
    ])


def regressor_pipeline(preprocessor):
    return Pipeline([
        ("preprocessor", preprocessor),
        ("regressor", RandomForestRegressor(
            n_estimators=300,
            random_state=42,
            n_jobs=-1
        ))
    ])


def train_classifier(X, target, preprocessor, name):
    valid = target.notna()
    X = X.loc[valid].copy()
    y = target.loc[valid].astype(str).str.strip()

    valid = y.ne("") & y.str.lower().ne("nan")
    X, y = X.loc[valid], y.loc[valid]

    if y.nunique() < 2:
        raise ValueError(f"{name} needs at least two target classes.")

    encoder = LabelEncoder()
    encoded = encoder.fit_transform(y)

    counts = pd.Series(encoded).value_counts()
    stratify = encoded if counts.min() >= 2 else None

    X_train, X_test, y_train, y_test = train_test_split(
        X, encoded, test_size=0.2, random_state=42,
        stratify=stratify
    )

    model = classifier_pipeline(preprocessor)
    model.fit(X_train, y_train)

    prediction = model.predict(X_test)
    print(f"{name} accuracy: {accuracy_score(y_test, prediction):.3f}")

    return model, encoder


def train_regressor(X, target, preprocessor, name):
    target = pd.to_numeric(target, errors="coerce")
    valid = target.notna() & X.notna().all(axis=1)
    X, y = X.loc[valid].copy(), target.loc[valid]

    if len(X) < 5:
        raise ValueError(f"Not enough valid rows to train {name}.")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    model = regressor_pipeline(preprocessor)
    model.fit(X_train, y_train)

    prediction = model.predict(X_test)
    print(f"{name} MAE: {mean_absolute_error(y_test, prediction):.3f}")

    return model


# ==========================================
# 1. MEDICATION MODEL
# ==========================================

print("\nTraining medication model...")

medication_model, medication_encoder = train_classifier(
    df[medication_features],
    df["Recommended_Medication"],
    med_preprocessor,
    "Medication"
)

joblib.dump(medication_model, BACKEND_PATH / "medication_model.pkl")
joblib.dump(medication_encoder, BACKEND_PATH / "medication_encoder.pkl")


# ==========================================
# 2. DOSAGE MODEL
# ==========================================

print("\nTraining dosage model...")

dosage_model = train_regressor(
    df[treatment_features],
    df["Dosage_mg"],
    treatment_preprocessor,
    "Dosage"
)

joblib.dump(dosage_model, BACKEND_PATH / "dosage_model.pkl")


# ==========================================
# 3. DURATION MODEL
# ==========================================

print("\nTraining duration model...")

duration_model = train_regressor(
    df[treatment_features],
    df["Duration_days"],
    treatment_preprocessor,
    "Duration"
)

joblib.dump(duration_model, BACKEND_PATH / "duration_model.pkl")


# ==========================================
# 4. EFFECTIVENESS MODEL
# ==========================================

print("\nTraining effectiveness model...")

effectiveness_model, effectiveness_encoder = train_classifier(
    df[treatment_features],
    df["Treatment_Effectiveness"],
    treatment_preprocessor,
    "Effectiveness"
)

joblib.dump(
    effectiveness_model,
    BACKEND_PATH / "effectiveness_model.pkl"
)
joblib.dump(
    effectiveness_encoder,
    BACKEND_PATH / "effectiveness_encoder.pkl"
)


# ==========================================
# 5. ADVERSE-REACTION MODEL
# ==========================================

print("\nTraining adverse-reaction model...")

adverse_target = (
    df["Adverse_Reactions"]
    .astype("string")
    .str.strip()
    .str.lower()
    .map({"no": 0, "yes": 1})
)

adverse_model, _ = train_classifier(
    df[treatment_features],
    adverse_target,
    treatment_preprocessor,
    "Adverse reaction"
)

joblib.dump(adverse_model, BACKEND_PATH / "adverse_model.pkl")


print("\n" + "=" * 55)
print("ALL FIVE MODELS TRAINED")
print("=" * 55)

for filename in [
    "medication_model.pkl",
    "medication_encoder.pkl",
    "dosage_model.pkl",
    "duration_model.pkl",
    "effectiveness_model.pkl",
    "effectiveness_encoder.pkl",
    "adverse_model.pkl"
]:
    print(f"Created: backend/{filename}")

print(
    "\nNote: dosage and duration are experimental model estimates, "
    "not clinical prescriptions."
)
