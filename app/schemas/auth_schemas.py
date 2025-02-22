from typing import Optional
from pydantic import BaseModel, EmailStr


class UserRegisterSchema(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_superuser: bool = False


class ForgotPasswordSchema(BaseModel):
    email: str


class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str


class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
