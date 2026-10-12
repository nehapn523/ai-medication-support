import pandas as pd
import numpy as np
from pathlib import Path


# ==========================================
# PATHS
# ==========================================

ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = ROOT / "dataset" / "personalized_medication.csv"

OUTPUT_PATH = ROOT / "dataset" / "processed_medication.csv"


# ==========================================
# LOAD DATA
# ==========================================

print("Loading dataset...")

df = pd.read_csv(DATA_PATH)


print("\nDataset shape:")
print(df.shape)


print("\nOriginal columns:")
print(df.columns.tolist())


# ==========================================
# CHECK EXPECTED COLUMNS
# ==========================================

expected_columns = [
    "Patient_ID",
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
    "Dosage",
    "Duration",
    "Treatment_Effectiveness",
    "Adverse_Reactions",
    "Recovery_Time_Days"
]


missing_columns = [
    col
    for col in expected_columns
    if col not in df.columns
]


if missing_columns:

    print("\nMissing columns:")

    for col in missing_columns:
        print(col)

    raise ValueError(
        "Dataset columns do not match expected schema."
    )


# ==========================================
# CONVERT STRING MISSING VALUES
# ==========================================

missing_strings = [
    "",
    "None",
    "none",
    "NULL",
    "null",
    "NaN",
    "nan"
]


for column in df.columns:

    if df[column].dtype == "object":

        df[column] = df[column].replace(
            missing_strings,
            np.nan
        )


# ==========================================
# NUMERIC COLUMNS
# ==========================================

numeric_columns = [
    "Age",
    "Weight_kg",
    "Height_cm",
    "BMI",
    "Recovery_Time_Days"
]


for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )


# ==========================================
# DOSAGE
# ==========================================

# Example:
# "500 mg" -> 500
# "200 mg" -> 200
# NaN -> NaN

df["Dosage_mg"] = (
    df["Dosage"]
    .astype(str)
    .str.extract(r"(\d+\.?\d*)")[0]
)


df["Dosage_mg"] = pd.to_numeric(
    df["Dosage_mg"],
    errors="coerce"
)


# ==========================================
# DURATION
# ==========================================

# Example:
# "30 days" -> 30
# "10 days" -> 10
# "7 days" -> 7

df["Duration_days"] = (
    df["Duration"]
    .astype(str)
    .str.extract(r"(\d+\.?\d*)")[0]
)


df["Duration_days"] = pd.to_numeric(
    df["Duration_days"],
    errors="coerce"
)


# ==========================================
# BMI CATEGORY
# ==========================================

def bmi_category(bmi):

    if pd.isna(bmi):
        return "Unknown"

    if bmi < 18.5:
        return "Underweight"

    elif bmi < 25:
        return "Normal"

    elif bmi < 30:
        return "Overweight"

    else:
        return "Obese"


df["BMI_Category"] = df["BMI"].apply(
    bmi_category
)


# ==========================================
# AGE CATEGORY
# ==========================================

def age_category(age):

    if age < 18:
        return "Child"

    elif age < 40:
        return "Young Adult"

    elif age < 60:
        return "Middle Aged"

    elif age < 75:
        return "Senior"

    else:
        return "Elderly"


df["Age_Category"] = df["Age"].apply(
    age_category
)


# ==========================================
# ADVERSE REACTION TARGET
# ==========================================

df["Adverse_Risk"] = (
    df["Adverse_Reactions"]
    .map({
        "Yes": 1,
        "No": 0
    })
)


# ==========================================
# FILL INPUT MISSING VALUES
# ==========================================

categorical_columns = [

    "Gender",
    "Chronic_Conditions",
    "Drug_Allergies",
    "Genetic_Disorders",
    "Diagnosis",
    "Symptoms"
]


for column in categorical_columns:

    df[column] = df[column].fillna(
        "Unknown"
    )


# Numeric missing values

for column in [
    "Age",
    "Weight_kg",
    "Height_cm",
    "BMI",
    "Recovery_Time_Days",
    "Dosage_mg",
    "Duration_days"
]:

    df[column] = df[column].fillna(
        df[column].median()
    )


# ==========================================
# SAVE
# ==========================================

df.to_csv(
    OUTPUT_PATH,
    index=False
)


print("\nPreprocessing completed.")

print("\nProcessed shape:")
print(df.shape)

print("\nSaved:")
print(OUTPUT_PATH)


print("\nTreatment effectiveness:")
print(
    df[
        "Treatment_Effectiveness"
    ].value_counts()
)


print("\nAdverse reaction:")
print(
    df[
        "Adverse_Reactions"
    ].value_counts()
)


print("\nMedication:")
print(
    df[
        "Recommended_Medication"
    ].value_counts(
        dropna=False
    )
)