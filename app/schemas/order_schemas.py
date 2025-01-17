from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

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
    items: List[OrderItemOutSchema] = []

    class Config:
        orm_mode = True
