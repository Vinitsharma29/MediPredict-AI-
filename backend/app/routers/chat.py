import re

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.deps import get_current_user
from app.models.patient import Patient
from app.models.prediction import Prediction
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()

UNSAFE_PATTERNS = [
    r"\bdose\b",
    r"\bmg\b",
    r"\bml\b",
    r"\bprescrib\w*\b",
    r"\bantibiotic\b",
    r"\bsteroid\b",
    r"\binsulin\b",
    r"\bwarfarin\b",
    r"\bwhat drug\b",
]


def _is_unsafe(text: str) -> bool:
    t = text.lower()
    return any(re.search(p, t) for p in UNSAFE_PATTERNS)


def _latest_preds(db: Session, patient_id: int) -> list[Prediction]:
    preds = db.scalars(
        select(Prediction)
        .where(Prediction.patient_id == patient_id)
        .order_by(Prediction.created_at.desc())
        .limit(5)
    ).all()
    return preds


@router.post("/", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if _is_unsafe(payload.message):
        return ChatResponse(
            response=(
                "I can’t provide medication selection or dosing. "
                "I can summarize risk factors, suggest diagnostic tests, and draft clinician-facing notes."
            ),
            safety="blocked_medical_dosing",
        )

    context = ""
    if payload.patient_id is not None:
        patient = db.get(Patient, payload.patient_id)
        if patient and (user.role == "doctor" or patient.owner_user_id == user.id):
            preds = _latest_preds(db, patient.id)
            if preds:
                lines = []
                for p in preds:
                    lines.append(f"- {p.disease}: {p.risk_level} ({p.probability:.0%})")
                context = "Recent AI predictions:\n" + "\n".join(lines)

    msg = payload.message.strip().lower()

    if "interpret" in msg or "explain" in msg:
        reply = (
            "Clinical interpretation (non-prescriptive):\n"
            "- Correlate symptoms with vitals and ECG/labs.\n"
            "- Treat AI as a risk flag; confirm with guideline-based testing.\n"
        )
    elif "symptom" in msg:
        reply = (
            "Symptom triage tips (non-emergency):\n"
            "- Screen red flags: chest pain, severe breathlessness, syncope, neuro deficits.\n"
            "- If red flags present, urgent evaluation is recommended.\n"
        )
    else:
        reply = (
            "I can help with: (1) summarizing risk drivers from SHAP, (2) suggesting tests/specialist, "
            "(3) drafting patient-friendly explanation, (4) clinician note templates.\n"
            "Ask: 'Explain why this risk is high' or 'Suggest tests for this case'."
        )

    if context:
        reply = context + "\n\n" + reply

    reply += "\n\nSafety note: This assistant does not replace clinical judgment."
    return ChatResponse(response=reply, safety="ok")
