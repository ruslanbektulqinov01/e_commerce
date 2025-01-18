# app/models/__init__.py
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.user import User

# For convenient import of all models
__all__ = ["Product", "Order", "OrderItem", "User"]