from pydantic import ConfigDict, BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: str = None
    is_active: bool = True
    is_verified: bool = False
    is_superuser: bool = False

class UserCreateSchema(UserBase):
    password: str

class UserUpdateSchema(BaseModel):
    email: str = None
    password: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    is_superuser: Optional[bool] = None

class UserOutSchema(UserBase):
    id: int
