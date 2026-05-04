from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class MeResponse(BaseModel):
    id: int
    email: EmailStr
    role: str
<<<<<<< HEAD
    full_name: str | None = None
=======
    full_name: str | None = None
>>>>>>> 37f8f4a638f6f6a45437c6c153e45685cab00099
