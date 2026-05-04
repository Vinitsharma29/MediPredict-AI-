from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.core.security import decrypt_text
from app.ml.adapters import patient_to_features
from app.ml.engine import predict as ml_predict
from app.models.alert import Alert
from app.models.patient import Patient
from app.models.prediction import Prediction
from app.models.user import User
from app.pdf import build_pdf
from app.recommendations import recommend
from app.schemas.prediction import PredictRequest, PredictionOut

router = APIRouter()


def _is_emergency(risk_level: str, probability: float) -> bool:
    return risk_level == "High" or probability >= 0.70


def _pred_out(p: Prediction, alert_flag: bool, alert_id: int | None) -> PredictionOut:
    return PredictionOut(
        id=p.id,
        patient_id=p.patient_id,
        disease=p.disease,
        model_name=p.model_name,
        risk_level=p.risk_level,
        probability=p.probability,
        feature_importance=p.feature_importance,
        shap_values=p.shap_values,
        recommendations=p.recommendations,
        alert_flag=alert_flag,
        alert_id=alert_id,
    )


@router.post("/run", response_model=PredictionOut)
def run_prediction(
    payload: PredictRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    patient = db.get(Patient, payload.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if user.role != "doctor" and patient.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    patient_dict = {
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "symptoms": patient.symptoms,
        "vitals": patient.vitals,
        "medical_history": decrypt_text(patient.medical_history_enc),
    }

    features = patient_to_features(payload.disease, patient_dict)
    result = ml_predict(payload.disease, features)
    rec = recommend(payload.disease, result["risk_level"], result["probability"])

    pred = Prediction(
        patient_id=patient.id,
        disease=payload.disease,
        model_name=result["model_name"],
        risk_level=result["risk_level"],
        probability=result["probability"],
        features=features,
        feature_importance=result["feature_importance"],
        shap_values=result["shap_values"],
        recommendations=rec,
    )
    db.add(pred)
    db.commit()
    db.refresh(pred)

    alert_flag = _is_emergency(pred.risk_level, pred.probability)
    alert_id: int | None = None

    if alert_flag:
        existing = db.scalar(
            select(Alert)
            .where(Alert.patient_id == patient.id)
            .where(Alert.status == "active")
            .order_by(Alert.timestamp.desc())
            .limit(1)
        )
        if existing:
            alert_id = existing.alert_id
        else:
            alert = Alert(patient_id=patient.id, risk_level=pred.risk_level, probability=pred.probability, status="active")
            db.add(alert)
            db.commit()
            db.refresh(alert)
            alert_id = alert.alert_id

    return _pred_out(pred, alert_flag, alert_id)


@router.get("/by-patient/{patient_id}", response_model=list[PredictionOut])
def list_predictions(
    patient_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if user.role != "doctor" and patient.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    preds = db.scalars(
        select(Prediction)
        .where(Prediction.patient_id == patient_id)
        .order_by(Prediction.created_at.desc())
    ).all()

    out: list[PredictionOut] = []
    for p in preds:
        alert_flag = _is_emergency(p.risk_level, p.probability)
        alert = None
        if alert_flag:
            alert = db.scalar(
                select(Alert)
                .where(Alert.patient_id == patient_id)
                .where(Alert.status == "active")
                .order_by(Alert.timestamp.desc())
                .limit(1)
            )
        out.append(_pred_out(p, alert_flag, alert.alert_id if alert else None))

    return out


@router.get("/{prediction_id}/report.pdf")
def download_prediction_report(
    prediction_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    pred = db.get(Prediction, prediction_id)
    if not pred:
        raise HTTPException(status_code=404, detail="Not found")

    patient = db.get(Patient, pred.patient_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if user.role != "doctor" and patient.owner_user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    patient_dict = {
        "name": patient.name,
        "age": patient.age,
        "gender": patient.gender,
        "symptoms": patient.symptoms,
        "vitals": patient.vitals,
        "medical_history": decrypt_text(patient.medical_history_enc),
    }

    pred_dict = {
        "disease": pred.disease,
        "risk_level": pred.risk_level,
        "probability": pred.probability,
        "feature_importance": pred.feature_importance,
        "recommendations": pred.recommendations,
    }

    pdf_bytes = build_pdf(patient_dict, pred_dict)
<<<<<<< HEAD
    return Response(content=pdf_bytes, media_type="application/pdf")
=======
    return Response(content=pdf_bytes, media_type="application/pdf")
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
