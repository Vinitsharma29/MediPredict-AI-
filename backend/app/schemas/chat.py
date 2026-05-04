from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    patient_id: int | None = None


class ChatResponse(BaseModel):
    response: str
<<<<<<< HEAD
    safety: str
=======
    safety: str
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
