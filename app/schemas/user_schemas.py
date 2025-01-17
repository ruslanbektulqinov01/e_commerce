from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False

class UserCreateSchema(UserBase):
    password: str

class UserUpdateSchema(BaseModel):
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserOutSchema(UserBase):
    id: int

    class Config:
        orm_mode = True
