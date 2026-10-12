
import sqlite3

from pathlib import Path


# ==========================================
# DATABASE CONFIGURATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "medication_support.db"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_connection():
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

def create_tables():
    conn = get_connection()

    try:
        cursor = conn.cursor()

        # --------------------------------------
        # PATIENTS TABLE
        # --------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                gender TEXT NOT NULL,
                weight_kg REAL NOT NULL,
                height_cm REAL NOT NULL,
                bmi REAL NOT NULL,
                chronic_conditions TEXT DEFAULT 'Unknown',
                drug_allergies TEXT DEFAULT 'Unknown',
                genetic_disorders TEXT DEFAULT 'Unknown',
                diagnosis TEXT NOT NULL,
                symptoms TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        # --------------------------------------
        # ANALYSES TABLE
        # --------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS analyses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                medication TEXT,
                dosage_mg REAL,
                duration_days REAL,
                predicted_medication TEXT,
                effectiveness TEXT,
                effectiveness_confidence REAL,
                adverse_risk TEXT,
                adverse_probability REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY (patient_id)
                    REFERENCES patients(id)
                    ON DELETE CASCADE
            )
            """
        )

        conn.commit()
        print("Database tables created successfully.")

    finally:
        conn.close()


# ==========================================
# TEST DATABASE
# ==========================================

if __name__ == "__main__":
    create_tables()
    print(f"Database location: {DATABASE_PATH}")
