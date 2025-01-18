from sqlalchemy import Column, Integer, String, Text, Float, Boolean
from app.db import Base

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False, default=0.0)
    is_active = Column(Boolean, default=True)
