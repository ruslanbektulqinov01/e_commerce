from typing import Optional
from pydantic import BaseModel


class ProductBase(BaseModel):
    name: str
    description: Optional[str] = None
    price: float
    is_active: bool = True


class ProductCreateSchema(ProductBase):
    pass


class ProductUpdateSchema(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    is_active: Optional[bool] = None


class ProductOutSchema(ProductBase):
    id: int

    class Config:
        from_attributes = True
