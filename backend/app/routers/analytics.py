from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import require_role
from app.models.prediction import Prediction

router = APIRouter()


@router.get("/distribution")
def distribution(db: Session = Depends(get_db), _=Depends(require_role("doctor"))):
    rows = db.execute(
        select(Prediction.disease, Prediction.risk_level, func.count(Prediction.id))
        .group_by(Prediction.disease, Prediction.risk_level)
    ).all()

    out = {}
    for disease, risk, cnt in rows:
        out.setdefault(disease, {})[risk] = int(cnt)
    return out


@router.get("/trends")
def trends(db: Session = Depends(get_db), _=Depends(require_role("doctor"))):
    since = datetime.utcnow() - timedelta(days=30)
    rows = db.execute(
        select(
            func.date(Prediction.created_at).label("day"),
            Prediction.risk_level,
            func.count(Prediction.id).label("cnt"),
        )
        .where(Prediction.created_at >= since)
        .group_by(func.date(Prediction.created_at), Prediction.risk_level)
        .order_by(func.date(Prediction.created_at))
    ).all()

    points = {}
    for day, risk, cnt in rows:
        key = str(day)
        points.setdefault(key, {"Low": 0, "Medium": 0, "High": 0})[risk] = int(cnt)

    return [{"day": day, **vals} for day, vals in sorted(points.items())]


@router.get("/high-risk")
def high_risk(db: Session = Depends(get_db), _=Depends(require_role("doctor"))):
    rows = db.execute(
        select(Prediction.patient_id, Prediction.disease, Prediction.risk_level, Prediction.probability, Prediction.created_at)
        .where(Prediction.risk_level == "High")
        .order_by(Prediction.created_at.desc())
        .limit(50)
    ).all()

    return [
        {
            "patient_id": int(pid),
            "disease": disease,
            "risk_level": risk,
            "probability": float(prob),
            "created_at": created_at.isoformat(),
        }
        for pid, disease, risk, prob, created_at in rows
<<<<<<< HEAD
    ]
=======
    ]
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
