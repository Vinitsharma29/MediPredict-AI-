from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user, require_role
from app.models.alert import Alert
from app.models.patient import Patient
from app.models.user import User

router = APIRouter()


class NotifyRequest(BaseModel):
    patient_id: int
    risk_level: str
    probability: float


@router.get("/active")
def list_active_alerts(db: Session = Depends(get_db), _=Depends(require_role("doctor"))):
    alerts = db.scalars(
        select(Alert).where(Alert.status == "active").order_by(Alert.timestamp.desc()).limit(200)
    ).all()

    out = []
    for a in alerts:
        p = db.get(Patient, a.patient_id)
        out.append(
            {
                "alert_id": a.alert_id,
                "patient_id": a.patient_id,
                "patient_name": p.name if p else "Unknown",
                "risk_level": a.risk_level,
                "probability": a.probability,
                "timestamp": a.timestamp.isoformat(),
                "status": a.status,
            }
        )
    return out


@router.post("/notify")
def notify_doctor(
    payload: NotifyRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    patient = db.get(Patient, payload.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if user.role != "doctor" and patient.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    existing = db.scalar(
        select(Alert)
        .where(Alert.patient_id == payload.patient_id)
        .where(Alert.status == "active")
        .order_by(Alert.timestamp.desc())
        .limit(1)
    )
    if existing:
        return {"alert_id": existing.alert_id, "status": existing.status}

    a = Alert(
        patient_id=payload.patient_id,
        risk_level=payload.risk_level,
        probability=payload.probability,
        status="active",
    )
    db.add(a)
    db.commit()
    db.refresh(a)
    return {"alert_id": a.alert_id, "status": a.status}


@router.post("/{alert_id}/resolve")
def resolve_alert(alert_id: int, db: Session = Depends(get_db), _=Depends(require_role("doctor"))):
    a = db.get(Alert, alert_id)
    if not a:
        raise HTTPException(status_code=404, detail="Not found")
    a.status = "resolved"
    db.commit()
<<<<<<< HEAD
    return {"ok": True}
=======
    return {"ok": True}
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
