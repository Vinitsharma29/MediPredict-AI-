from __future__ import annotations

from typing import Any


def recommend(disease: str, risk_level: str, probability: float) -> dict[str, Any]:
    tests = []
    specialist = []
    tips = []

    if disease == "heart":
        tests += ["ECG", "Lipid Profile", "Blood Pressure monitoring"]
        specialist += ["Cardiologist"]
        tips += ["Reduce salt", "Regular walking 30 min/day", "Stop smoking/alcohol moderation"]
        if risk_level in ("Medium", "High"):
            tests += ["Troponin (if symptomatic)", "Echocardiography"]
            tips += ["Urgent evaluation if chest pain / breathlessness worsens"]

    if disease == "diabetes":
        tests += ["HbA1c", "Fasting + Postprandial glucose"]
        specialist += ["Endocrinologist"]
        tips += ["Limit sugar/refined carbs", "Weight management", "Hydration"]
        if risk_level in ("Medium", "High"):
            tests += ["Urine microalbumin", "Eye examination (retinopathy screening)"]

    return {
        "risk_level": risk_level,
        "probability": probability,
        "suggested_tests": sorted(set(tests)),
        "suggested_specialists": sorted(set(specialist)),
        "lifestyle_tips": tips,
        "disclaimer": "AI support only. Final clinical decisions must be made by a licensed clinician.",
    }
