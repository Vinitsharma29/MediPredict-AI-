from pydantic import BaseModel


class DoctorDecisionRequest(BaseModel):
    prediction_id: int
    doctor_note: str | None = None
<<<<<<< HEAD
    doctor_decision: str  # approved | rejected
=======
    doctor_decision: str  # approved | rejected
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
