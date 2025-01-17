from pydantic import BaseModel, Field
from typing import List
from datetime import datetime
from dataclasses import dataclass, field

class OrderItemSchema(BaseModel):
    product_id: int
    quantity: int
    price: float

class OrderCreateSchema(BaseModel):
    items: List[OrderItemSchema]

class OrderItemOutSchema(OrderItemSchema):
    id: int

    class Config:
        orm_mode = True

class OrderOutSchema(BaseModel):
    id: int
    user_id: int
    created_at: datetime
    status: str
    items: List[OrderItemOutSchema] = field(default_factory=list)

    class Config:
        orm_mode = True
