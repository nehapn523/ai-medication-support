
// ==========================================
// API CONFIGURATION
// ==========================================

const API_URL = "https://ai-medication-support.onrender.com";

console.log("script.js loaded successfully!");


// ==========================================
// DOM HELPERS
// ==========================================

const getElement = (id) => document.getElementById(id);

function showMessage(elementId, message, isError = false) {
    const element = getElement(elementId);

    if (!element) {
        console.error(`Element not found: ${elementId}`);
        return;
    }

    element.textContent = message;
    element.className = isError
        ? "message error"
        : "message success";
}

function formatPercent(value) {
    if (
        value === null ||
        value === undefined ||
        !Number.isFinite(Number(value))
    ) {
        return "Unavailable";
    }

    return `${Number(value).toFixed(2)}%`;
}

function formatNumber(value, digits = 2) {
    if (
        value === null ||
        value === undefined ||
        !Number.isFinite(Number(value))
    ) {
        return "Unavailable";
    }

    return Number(value).toFixed(digits);
}


// ==========================================
// ERROR DIAGNOSTICS
// ==========================================

window.addEventListener("error", function (event) {
    console.error("JavaScript error:", event.message);
    console.error(
        "Location:",
        event.filename,
        "Line:",
        event.lineno
    );
});

window.addEventListener("unhandledrejection", function (event) {
    console.error(
        "Unhandled promise rejection:",
        event.reason
    );
});


// ==========================================
// API REQUEST HANDLER
// ==========================================

async function apiRequest(endpoint, options = {}) {
    let response;

    console.log("Sending API request:", endpoint);

    try {
        response = await fetch(`${API_URL}${endpoint}`, {
            ...options,
            headers: {
                "Content-Type": "application/json",
                ...(options.headers || {})
            }
        });
    } catch (error) {
        console.error("Backend connection error:", error);

        throw new Error(
            "Cannot connect to the backend. Make sure FastAPI is running at http://127.0.0.1:8000."
        );
    }

    const data = await response.json().catch(() => ({}));

    console.log("API response:", response.status, data);

    if (!response.ok) {
        const detail = data.detail;

        let message;

        if (typeof detail === "string") {
            message = detail;
        } else if (detail) {
            message = JSON.stringify(detail);
        } else {
            message = `Request failed with status ${response.status}`;
        }

        throw new Error(message);
    }

    return data;
}


// ==========================================
// AUTOMATIC BMI CALCULATION
// ==========================================

function calculateBMI() {
    const weightElement = getElement("weight");
    const heightElement = getElement("height");
    const bmiElement = getElement("bmi");

    if (!weightElement || !heightElement || !bmiElement) {
        console.error("BMI form elements are missing.");
        return;
    }

    const weight = Number(weightElement.value);
    const heightCm = Number(heightElement.value);

    if (
        weightElement.value.trim() !== "" &&
        heightElement.value.trim() !== "" &&
        Number.isFinite(weight) &&
        Number.isFinite(heightCm) &&
        weight > 0 &&
        heightCm > 0
    ) {
        const heightM = heightCm / 100;
        const bmi = weight / (heightM * heightM);

        bmiElement.value = bmi.toFixed(2);
    } else {
        bmiElement.value = "";
    }
}


// ==========================================
// INITIALIZE FRONTEND
// ==========================================

function initializeFrontend() {
    console.log("Initializing frontend...");

    const patientForm = getElement("patientForm");
    const analysisForm = getElement("analysisForm");

    if (!patientForm) {
        console.error(
            'Registration form not found. Check for id="patientForm" in index.html.'
        );
        return;
    }

    if (!analysisForm) {
        console.error(
            'Analysis form not found. Check for id="analysisForm" in index.html.'
        );
        return;
    }

    // ======================================
    // BMI EVENT LISTENERS
    // ======================================

    getElement("weight").addEventListener("input", calculateBMI);
    getElement("height").addEventListener("input", calculateBMI);


    // ======================================
    // PATIENT REGISTRATION
    // ======================================

    patientForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        console.log("Patient registration form submitted.");

        const button = getElement("registerButton");

        if (!button) {
            console.error("Register button not found.");
            showMessage(
                "registrationMessage",
                "Registration button could not be found.",
                true
            );
            return;
        }

        button.disabled = true;
        button.textContent = "Registering...";

        try {
            const patientData = {
                name: getElement("name").value.trim(),
                age: Number(getElement("age").value),
                gender: getElement("gender").value,
                weight_kg: Number(getElement("weight").value),
                height_cm: Number(getElement("height").value),

                chronic_conditions:
                    getElement("conditions").value.trim() || "Unknown",

                drug_allergies:
                    getElement("allergies").value.trim() || "Unknown",

                genetic_disorders:
                    getElement("genetic").value.trim() || "Unknown",

                diagnosis:
                    getElement("diagnosis").value.trim(),

                symptoms:
                    getElement("symptoms").value.trim()
            };

            console.log("Patient data prepared:", patientData);

            const result = await apiRequest("/patients", {
                method: "POST",
                body: JSON.stringify(patientData)
            });

            getElement("patientId").value = result.patient_id;

            showMessage(
                "registrationMessage",
                `Patient registered successfully! Patient ID: ${result.patient_id}. BMI: ${formatNumber(result.calculated_bmi)}`
            );

            showMessage(
                "analysisMessage",
                "You can now run the medication analysis."
            );

            console.log(
                "Patient registered successfully:",
                result
            );

        } catch (error) {
            console.error("Registration failed:", error);

            showMessage(
                "registrationMessage",
                `Registration failed: ${error.message}`,
                true
            );
        } finally {
            button.disabled = false;
            button.textContent = "Register Patient";
        }
    });


    // ======================================
    // RUN MEDICATION ANALYSIS
    // ======================================

    analysisForm.addEventListener("submit", async function (event) {
        event.preventDefault();

        console.log("Medication analysis form submitted.");

        const button = getElement("analyzeButton");
        const patientId = Number(getElement("patientId").value);

        if (!Number.isInteger(patientId) || patientId <= 0) {
            showMessage(
                "analysisMessage",
                "Please register a patient first and use the generated patient ID.",
                true
            );
            return;
        }

        button.disabled = true;
        button.textContent = "Analyzing...";

        getElement("resultsSection").hidden = true;

        try {
            const result = await apiRequest("/analyze", {
                method: "POST",
                body: JSON.stringify({
                    patient_id: patientId
                })
            });

            console.log("Analysis result:", result);

            displayResults(result);

            showMessage(
                "analysisMessage",
                "Analysis completed successfully."
            );

            getElement("resultsSection").hidden = false;

            getElement("resultsSection").scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        } catch (error) {
            console.error("Analysis failed:", error);

            showMessage(
                "analysisMessage",
                `Analysis failed: ${error.message}`,
                true
            );
        } finally {
            button.disabled = false;
            button.textContent = "Run Analysis";
        }
    });

    // Hide analysis results when the page first loads.
    getElement("resultsSection").hidden = true;

    console.log("Frontend initialized successfully.");
}


// ==========================================
// DISPLAY ANALYSIS RESULTS
// ==========================================

function displayResults(result) {
    getElement("resultBMI").textContent =
        formatNumber(result.calculated_bmi);

    getElement("resultMedication").textContent =
        result.predicted_medication ?? "Unavailable";

    getElement("resultMedicationConfidence").textContent =
        formatPercent(result.medication_confidence);

    getElement("resultDosage").textContent =
        `${formatNumber(result.predicted_dosage_mg)} mg (experimental estimate)`;

    getElement("resultDuration").textContent =
        `${formatNumber(result.predicted_duration_days)} days (experimental estimate)`;

    getElement("resultEffectiveness").textContent =
        result.treatment_effectiveness ?? "Unavailable";

    getElement("resultEffectivenessConfidence").textContent =
        formatPercent(result.effectiveness_confidence);

    getElement("resultRisk").textContent =
        result.adverse_risk ?? "Unavailable";

    getElement("resultProbability").textContent =
        formatPercent(result.adverse_probability);


    // ======================================
    // ALLERGY REVIEW
    // ======================================

    const safety = result.safety_check;

    getElement("resultSafety").textContent = safety
        ? `Status: ${safety.status}`
        : "Safety review unavailable.";

    const safetyList = getElement("safetyAlerts");
    safetyList.replaceChildren();

    if (safety && Array.isArray(safety.alerts)) {
        safety.alerts.forEach(function (alert) {
            const item = document.createElement("li");

            item.textContent =
                `${alert.level}: ${alert.message}`;

            safetyList.appendChild(item);
        });
    }


    // ======================================
    // FEATURE IMPORTANCE
    // ======================================

    const explanationList = getElement("explanationList");
    explanationList.replaceChildren();

    if (
        Array.isArray(result.explanation) &&
        result.explanation.length > 0
    ) {
        result.explanation.forEach(function (item) {
            const listItem = document.createElement("li");

            listItem.textContent =
                `${item.feature}: ${formatNumber(item.importance, 4)}`;

            explanationList.appendChild(listItem);
        });
    } else {
        const item = document.createElement("li");

        item.textContent =
            "Feature importance is unavailable.";

        explanationList.appendChild(item);
    }

    getElement("explanationNote").textContent =
        result.explanation_note ?? "";


    // ======================================
    // SAFETY LIMITATIONS
    // ======================================

    getElement("safetyNote").textContent =
        result.safety_note ??
        "These are experimental model outputs, not medical advice.";
}


// ==========================================
// START WHEN HTML IS READY
// ==========================================

if (document.readyState === "loading") {
    document.addEventListener(
        "DOMContentLoaded",
        initializeFrontend
    );
} else {
    initializeFrontend();
}
