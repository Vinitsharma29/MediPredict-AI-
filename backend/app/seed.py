import random
from sqlalchemy import select

from app.core.db import SessionLocal
from app.core.security import encrypt_text, hash_password
from app.models.patient import Patient
from app.models.user import User

SYMPTOMS = [
    "chest_pain",
    "shortness_of_breath",
    "fatigue",
    "headache",
    "dizziness",
    "nausea",
    "blurred_vision",
    "frequent_urination",
    "increased_thirst",
    "palpitations",
    "swelling_legs",
    "fever",
    "cough",
    "abdominal_pain",
]


def _rand_vitals() -> dict:
    systolic = random.randint(100, 170)
    diastolic = random.randint(60, 110)
    return {
        "bp_systolic": systolic,
        "bp_diastolic": diastolic,
        "heart_rate": random.randint(55, 120),
        "fasting_sugar": random.randint(70, 220),
        "bmi": round(random.uniform(18.0, 38.0), 1),
    }


def seed_if_needed() -> None:
    db = SessionLocal()
    try:
        has_users = db.scalar(select(User.id).limit(1))
        if has_users:
            return

        doctor = User(
            email="doctor@medipredict.ai",
            hashed_password=hash_password("Doctor@123"),
            role="doctor",
            full_name="Dr. A. Sharma",
        )
        patient_user = User(
            email="patient@medipredict.ai",
            hashed_password=hash_password("Patient@123"),
            role="patient",
            full_name="Ravi Kumar",
        )
        db.add_all([doctor, patient_user])
        db.flush()

        demo_names = [
            "Ravi Kumar",
            "Ananya Singh",
            "Amit Patel",
            "Priya Iyer",
            "Suresh Nair",
            "Neha Verma",
            "Rahul Mehta",
            "Kavita Joshi",
            "Imran Khan",
            "Meera Das",
            "Arjun Rao",
            "Pooja Gupta",
            "Vikram Shah",
            "Sara Ali",
            "Deepak Yadav",
        ]
        genders = ["male", "female"]

        patients = []
        for i, name in enumerate(demo_names):
            vitals = _rand_vitals()
            symptoms = random.sample(SYMPTOMS, k=random.randint(2, 5))
            history = (
                "Hypertension" if vitals["bp_systolic"] > 140 else "No known hypertension"
            )
            owner = patient_user.id if i == 0 else None
            patients.append(
                Patient(
                    owner_user_id=owner,
                    name=name,
                    age=random.randint(22, 78),
                    gender=random.choice(genders),
                    symptoms={"selected": symptoms},
                    vitals=vitals,
                    medical_history_enc=encrypt_text(history),
                )
            )

        db.add_all(patients)
        db.commit()
    finally:
        db.close()
