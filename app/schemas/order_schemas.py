from typing import List
from pydantic import BaseModel
from datetime import datetime
from dataclasses import dataclass, field


class OrderItemSchema(BaseModel):
    product_id: int
    quantity: int


class OrderCreateSchema(BaseModel):
    # Admin yoki router user_id ni o'zi qo'shishi mumkin
    # Yoki current userga biriktiramiz:
    # Bu misolda user_id "controller"da o'zimiz set qilishimiz mumkin.
    items: List[OrderItemSchema]


class OrderItemOutSchema(BaseModel):
    id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


@dataclass
class OrderOutSchema(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: str
    total_price: float
    items: List[OrderItemOutSchema] = field(default_factory=list)

    class Config:
        from_attributes = True
