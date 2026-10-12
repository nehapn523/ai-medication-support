
# ==========================================
# BASIC ALLERGY SAFETY CHECK
# ==========================================

def check_safety(drug_allergies, predicted_medication):
    """
    Check a small set of configured allergy rules.

    This is a demonstration only. It is NOT a complete
    drug-allergy database or clinical safety checker.
    """

    allergies = str(drug_allergies or "").strip().lower()
    medication = str(predicted_medication or "").strip().lower()

    alerts = []

    # --------------------------------------
    # 1. CHECK FOR MISSING ALLERGY INFORMATION
    # --------------------------------------

    unknown_values = {
        "", "unknown", "none provided", "not provided",
        "not known", "n/a", "na"
    }

    if allergies in unknown_values:
        alerts.append({
            "level": "REVIEW",
            "message": (
                "Allergy information is missing or unclear. "
                "Verify allergies with a qualified healthcare professional."
            )
        })

    # --------------------------------------
    # 2. CHECK PENICILLIN / AMOXICILLIN RULE
    # --------------------------------------

    penicillin_allergy = (
        "penicillin" in allergies
        or "amoxicillin allergy" in allergies
    )

    amoxicillin_selected = "amoxicillin" in medication

    if penicillin_allergy and amoxicillin_selected:
        alerts.append({
            "level": "HIGH",
            "message": (
                "Potential conflict: the recorded penicillin allergy "
                "may be relevant to the predicted amoxicillin result. "
                "Do not use this prediction to make a treatment decision; "
                "seek professional medical review."
            )
        })

    # --------------------------------------
    # 3. GENERAL REVIEW MESSAGE
    # --------------------------------------

    if not alerts:
        alerts.append({
            "level": "REVIEW",
            "message": (
                "No configured allergy rule was triggered. "
                "This does not confirm that the predicted medicine is safe."
            )
        })

    # --------------------------------------
    # 4. FINAL STATUS
    # --------------------------------------

    high_alert = any(
        alert["level"] == "HIGH"
        for alert in alerts
    )

    return {
        "status": "HIGH ALERT" if high_alert else "REVIEW REQUIRED",
        "alerts": alerts,
        "checked_medication": predicted_medication,
        "clinical_safety_confirmed": False
    }
