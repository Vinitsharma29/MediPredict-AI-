from pydantic import BaseModel


class DoctorDecisionRequest(BaseModel):
    prediction_id: int
    doctor_note: str | None = None
    doctor_decision: str  # approved | rejected
