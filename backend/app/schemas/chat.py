from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    patient_id: int | None = None


class ChatResponse(BaseModel):
    response: str
    safety: str
