from typing import Optional
from pydantic import BaseModel


class UserBase(BaseModel):
    email: str
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False


class UserOutSchema(UserBase):
    id: int

    class Config:
        from_attributes = True  # pydantic v2


class UserUpdateSchema(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None
