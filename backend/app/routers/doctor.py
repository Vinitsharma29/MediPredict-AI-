from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_role
from app.core.security import decrypt_text
from app.models.alert import Alert
from app.models.patient import Patient
from app.models.prediction import Prediction
from app.models.report import Report
from app.schemas.doctor import DoctorDecisionRequest

router = APIRouter()


def _has_active_alert(db: Session, patient_id: int) -> Alert | None:
    return db.scalar(
        select(Alert)
        .where(Alert.patient_id == patient_id)
        .where(Alert.status == "active")
        .order_by(Alert.timestamp.desc())
        .limit(1)
    )


@router.get("/patients")
def doctor_patients(db: Session = Depends(get_db), _=Depends(require_role("doctor"))):
    patients = db.scalars(select(Patient).order_by(Patient.created_at.desc()).limit(300)).all()

    out = []
    for p in patients:
        latest = db.scalar(
            select(Prediction)
            .where(Prediction.patient_id == p.id)
            .order_by(Prediction.created_at.desc())
            .limit(1)
        )
        alert = _has_active_alert(db, p.id)

        out.append(
            {
                "id": p.id,
                "name": p.name,
                "age": p.age,
                "gender": p.gender,
                "created_at": p.created_at.isoformat(),
                "has_active_alert": bool(alert),
                "active_alert_id": alert.alert_id if alert else None,
                "latest_prediction": None
                if not latest
                else {
                    "id": latest.id,
                    "disease": latest.disease,
                    "risk_level": latest.risk_level,
                    "probability": latest.probability,
                    "created_at": latest.created_at.isoformat(),
                    "doctor_decision": latest.doctor_decision,
                },
            }
        )

    # Critical patients first
    out.sort(key=lambda x: (not x.get("has_active_alert", False), x.get("created_at", "")))
    return out


@router.get("/patient/{patient_id}")
def doctor_patient_detail(
    patient_id: int,
    db: Session = Depends(get_db),
    _=Depends(require_role("doctor")),
):
    p = db.get(Patient, patient_id)
    if not p:
        raise HTTPException(status_code=404, detail="Not found")

    preds = db.scalars(
        select(Prediction)
        .where(Prediction.patient_id == patient_id)
        .order_by(Prediction.created_at.desc())
    ).all()
    reports = db.scalars(
        select(Report)
        .where(Report.patient_id == patient_id)
        .order_by(Report.created_at.desc())
    ).all()

    alert = _has_active_alert(db, patient_id)

    return {
        "patient": {
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "gender": p.gender,
            "symptoms": list((p.symptoms or {}).get("selected", [])),
            "vitals": p.vitals or {},
            "medical_history": decrypt_text(p.medical_history_enc),
        },
        "active_alert": None
        if not alert
        else {
            "alert_id": alert.alert_id,
            "risk_level": alert.risk_level,
            "probability": alert.probability,
            "timestamp": alert.timestamp.isoformat(),
            "status": alert.status,
        },
        "predictions": [
            {
                "id": pr.id,
                "disease": pr.disease,
                "risk_level": pr.risk_level,
                "probability": pr.probability,
                "feature_importance": pr.feature_importance,
                "recommendations": pr.recommendations,
                "doctor_note": pr.doctor_note,
                "doctor_decision": pr.doctor_decision,
                "created_at": pr.created_at.isoformat(),
            }
            for pr in preds
        ],
        "reports": [
            {"id": r.id, "filename": r.filename, "mimetype": r.mimetype, "created_at": r.created_at.isoformat()}
            for r in reports
        ],
    }


@router.post("/prediction/decision")
def doctor_decision(
    payload: DoctorDecisionRequest,
    db: Session = Depends(get_db),
    _=Depends(require_role("doctor")),
):
    pred = db.get(Prediction, payload.prediction_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Prediction not found")

    if payload.doctor_decision not in ("approved", "rejected"):
        raise HTTPException(status_code=400, detail="doctor_decision must be approved/rejected")

    pred.doctor_note = payload.doctor_note
    pred.doctor_decision = payload.doctor_decision
    db.commit()

    return {"ok": True}
