import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

DATA_PATH = ROOT / "dataset" / "processed_medication.csv"

df = pd.read_csv(DATA_PATH)


print("=" * 60)
print("EXPLORATORY DATA ANALYSIS")
print("=" * 60)


print("\nShape:")
print(df.shape)


print("\nMissing values:")
print(
    df.isnull().sum()
)


print("\nTreatment effectiveness:")
print(
    df[
        "Treatment_Effectiveness"
    ].value_counts()
)


print("\nAdverse reactions:")
print(
    df[
        "Adverse_Reactions"
    ].value_counts()
)


print("\nMedication:")
print(
    df[
        "Recommended_Medication"
    ].value_counts()
)


# ==========================================
# EFFECTIVENESS
# ==========================================

plt.figure(figsize=(8, 5))

sns.countplot(
    data=df,
    x="Treatment_Effectiveness"
)

plt.title(
    "Treatment Effectiveness Distribution"
)

plt.xticks(rotation=20)

plt.tight_layout()

plt.savefig(
    ROOT / "effectiveness.png"
)

plt.show()


# ==========================================
# ADVERSE REACTIONS
# ==========================================

plt.figure(figsize=(7, 5))

sns.countplot(
    data=df,
    x="Adverse_Reactions"
)

plt.title(
    "Adverse Reaction Distribution"
)

plt.tight_layout()

plt.savefig(
    ROOT / "adverse_reactions.png"
)

plt.show()


# ==========================================
# MEDICATION
# ==========================================

plt.figure(figsize=(8, 5))

sns.countplot(
    data=df,
    x="Recommended_Medication"
)

plt.title(
    "Medication Distribution"
)

plt.xticks(rotation=20)

plt.tight_layout()

plt.savefig(
    ROOT / "medications.png"
)

plt.show()


# ==========================================
# AGE
# ==========================================

plt.figure(figsize=(8, 5))

sns.histplot(
    data=df,
    x="Age",
    bins=20,
    kde=True
)

plt.title(
    "Patient Age Distribution"
)

plt.tight_layout()

plt.savefig(
    ROOT / "age_distribution.png"
)

plt.show()


# ==========================================
# BMI
# ==========================================

plt.figure(figsize=(8, 5))

sns.histplot(
    data=df,
    x="BMI",
    bins=20,
    kde=True
)

plt.title(
    "BMI Distribution"
)

plt.tight_layout()

plt.savefig(
    ROOT / "bmi_distribution.png"
)

plt.show()