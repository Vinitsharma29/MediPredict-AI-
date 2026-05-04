from pydantic import BaseModel, Field


class PatientCreate(BaseModel):
    name: str
    age: int = Field(ge=0, le=120)
    gender: str
    symptoms: list[str]
    vitals: dict
    medical_history: str | None = None


class PatientOut(BaseModel):
    id: int
    name: str
    age: int
    gender: str
    symptoms: list[str]
    vitals: dict
<<<<<<< HEAD
    medical_history: str | None = None
=======
    medical_history: str | None = None
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
