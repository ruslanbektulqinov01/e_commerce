from pydantic import ConfigDict, BaseModel
from typing import Optional

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
    model_config = ConfigDict(from_attributes=True)
