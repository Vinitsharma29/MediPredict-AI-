import random
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user, require_role
from app.core.security import decrypt_text, encrypt_text
from app.models.patient import Patient
from app.models.user import User
from app.schemas.patient import PatientCreate, PatientOut
from app.seed import SYMPTOMS

router = APIRouter()


def _to_out(p: Patient) -> PatientOut:
    return PatientOut(
        id=p.id,
        name=p.name,
        age=p.age,
        gender=p.gender,
        symptoms=list(p.symptoms.get("selected", [])) if isinstance(p.symptoms, dict) else [],
        vitals=p.vitals or {},
        medical_history=decrypt_text(p.medical_history_enc),
    )


@router.get("/", response_model=list[PatientOut])
def list_patients(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role == "doctor":
        rows = db.scalars(select(Patient).order_by(Patient.created_at.desc()).limit(200)).all()
    else:
        rows = db.scalars(
            select(Patient).where(Patient.owner_user_id == user.id).order_by(Patient.created_at.desc())
        ).all()
    return [_to_out(p) for p in rows]


@router.post("/", response_model=PatientOut)
def create_patient(
    payload: PatientCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    owner_user_id = user.id if user.role == "patient" else None
    p = Patient(
        owner_user_id=owner_user_id,
        name=payload.name,
        age=payload.age,
        gender=payload.gender,
        symptoms={"selected": payload.symptoms},
        vitals=payload.vitals,
        medical_history_enc=encrypt_text(payload.medical_history),
    )
    db.add(p)
    db.commit()
    db.refresh(p)
    return _to_out(p)


@router.get("/{patient_id}", response_model=PatientOut)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")
    if user.role != "doctor" and p.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    return _to_out(p)


@router.get("/simulate/case")
def simulate_patient_case(user: User = Depends(require_role("doctor", "patient"))):
    age = random.randint(25, 80)
    gender = random.choice(["male", "female"])
    symptoms = random.sample(SYMPTOMS, k=random.randint(2, 5))
    vitals = {
        "bp_systolic": random.randint(95, 180),
        "bp_diastolic": random.randint(55, 115),
        "heart_rate": random.randint(50, 130),
        "fasting_sugar": random.randint(70, 260),
        "bmi": round(random.uniform(18.0, 40.0), 1),
        "cholesterol": random.randint(120, 320),
    }
    return {
        "name": random.choice(["Demo Patient", "Walk-in Case", "OPD Patient"]),
        "age": age,
        "gender": gender,
        "symptoms": symptoms,
        "vitals": vitals,
        "medical_history": "Auto-generated demo case for hackathon workflow.",
    }
