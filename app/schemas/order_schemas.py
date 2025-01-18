from pydantic import ConfigDict, BaseModel, Field
from typing import List
from datetime import datetime
from dataclasses import dataclass, field

class OrderItemSchema(BaseModel):
    product_id: int
    quantity: int

class OrderCreateSchema(BaseModel):
    user_id: int
    items: List[OrderItemSchema]

class OrderItemOutSchema(OrderItemSchema):
    product_id: int
    quantity: int
    price: float

class OrderOutSchema(BaseModel):
    id: int
    user_id: int
    total_price: float
    items: List[OrderItemOutSchema]