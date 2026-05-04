from __future__ import annotations

from typing import Any


def _yn(flag: bool) -> int:
    return 1 if flag else 0


def _symptoms_set(symptoms: dict | list[str] | None) -> set[str]:
    if symptoms is None:
        return set()
    if isinstance(symptoms, dict):
        return set(symptoms.get("selected", []) or [])
    if isinstance(symptoms, list):
        return set(symptoms)
    return set()


def patient_to_features(disease: str, patient: dict[str, Any]) -> dict[str, float]:
    age = float(patient.get("age") or 0)
    gender = str(patient.get("gender") or "").lower()

    vitals = patient.get("vitals") or {}
    bp_sys = float(vitals.get("bp_systolic") or 120)
    bp_dia = float(vitals.get("bp_diastolic") or 80)
    sugar = float(vitals.get("fasting_sugar") or vitals.get("glucose") or 100)
    hr = float(vitals.get("heart_rate") or 75)
    bmi = float(vitals.get("bmi") or 25)
    chol = float(vitals.get("cholesterol") or 200)

    symptoms = _symptoms_set(patient.get("symptoms"))

    if disease == "heart":
        # Common heart.csv schema (UCI-style)
        # age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
        sex = 1.0 if gender.startswith("m") else 0.0
        cp = 2.0 if "chest_pain" in symptoms else 0.0
        trestbps = bp_sys
        fbs = float(_yn(sugar >= 120))
        thalach = float(max(60.0, min(202.0, 170.0 - age)))
        exang = float(_yn("shortness_of_breath" in symptoms))
        oldpeak = 1.0 if "fatigue" in symptoms else 0.0

        return {
            "age": age,
            "sex": sex,
            "cp": cp,
            "trestbps": trestbps,
            "chol": chol,
            "fbs": fbs,
            "restecg": 1.0,
            "thalach": thalach,
            "exang": exang,
            "oldpeak": oldpeak,
            "slope": 1.0,
            "ca": 0.0,
            "thal": 2.0,
        }

    if disease == "diabetes":
        # Common diabetes.csv schema (Pima)
        # Pregnancies, Glucose, BloodPressure, SkinThickness, Insulin, BMI, DiabetesPedigreeFunction, Age
        pregnancies = 0.0
        if not gender.startswith("m"):
            pregnancies = 1.0 if age >= 25 else 0.0
        return {
            "Pregnancies": pregnancies,
            "Glucose": sugar,
            "BloodPressure": bp_dia,
            "SkinThickness": 20.0,
            "Insulin": 80.0,
            "BMI": bmi,
            "DiabetesPedigreeFunction": 0.6,
            "Age": age,
        }

<<<<<<< HEAD
    raise ValueError("unknown disease")
=======
    raise ValueError("unknown disease")
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
