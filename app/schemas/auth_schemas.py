from typing import Optional

from pydantic import BaseModel, EmailStr

class UserLoginSchema(BaseModel):
    email: str
    password: str

class UserRegisterSchema(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_superuser: bool = False

class ResendVerificationSchema(BaseModel):
    email: str

class ForgotPasswordSchema(BaseModel):
    email: str

class ResetPasswordSchema(BaseModel):
    token: str
    new_password: str

class TokenSchema(BaseModel):
    access_token: str
    token_type: str = "bearer"
