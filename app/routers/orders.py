from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.db import get_async_session
from app.models.order import Order, OrderItem
from app.models.user import User
from app.models.product import Product
from app.schemas.order_schemas import (
    OrderCreateSchema, OrderOutSchema
)
from app.services.security import get_current_user

orders_router = APIRouter(prefix="/api/orders", tags=["Orders"])

@orders_router.get("/", response_model=List[OrderOutSchema])
async def get_all_orders(
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # Admin check
    user = await session.scalar(select(User).where(User.email == current_user_email))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    # all orders
    orders = (await session.scalars(select(Order))).all()
    result_list = []
    for o in orders:
        # o _mapping bo'lib keladi, uni dict sifatida ishlatish:
        order_dict = vars(o)
        order = Order(**order_dict)

        items = (await session.scalars(select(OrderItem).where(OrderItem.order_id == order.id))).all()
        order.items = items
        result_list.append(order)
    return result_list

@orders_router.get("/{order_id}", response_model=OrderOutSchema)
async def get_order(
    order_id: int,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # order topish
    order = await session.scalar(select(Order).where(Order.id == order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # userni topish
    user = await session.scalar(select(User).where(User.email == current_user_email))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # ruxsat tekshirish
    if not user.is_superuser and order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # itemlar
    items = await session.scalars(select(OrderItem).where(OrderItem.order_id == order.id))
    order.items = items.all()

    return order

@orders_router.post("/", response_model=OrderOutSchema)
async def create_order(
    order_data: OrderCreateSchema,
    session: AsyncSession = Depends(get_async_session)
):
    # Calculate total price
    total_price = 0
    items = []
    for item in order_data.items:
        result = await session.execute(
            select(Product).where(Product.id == item.product_id)
        )
        product = result.scalar_one_or_none()
        if not product:
            raise HTTPException(status_code=404, detail=f"Product with id {item.product_id} not found")
        total_price += product.price * item.quantity
        items.append(OrderItem(product_id=item.product_id, quantity=item.quantity, price=product.price))

    # Create new order
    new_order = Order(user_id=order_data.user_id, total_price=total_price, items=items)
    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)
    return new_order

@orders_router.get("/customer/{customer_id}", response_model=List[OrderOutSchema])
async def get_customer_orders(
    customer_id: int,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # current user
    user = await session.scalar(select(User).where(User.email == current_user_email))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not user.is_superuser and user.id != customer_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    orders = (await session.scalars(select(Order).where(Order.user_id == customer_id))).all()
    result_list = []
    for o in orders:
        order_dict = vars(o)
        order = Order(**order_dict)
        items = (await session.scalars(select(OrderItem).where(OrderItem.order_id == order.id))).all()
        order.items = items
        result_list.append(order)
    return result_list

@orders_router.get("/{order_id}/status")
async def get_order_status(
    order_id: int,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    order = await session.scalar(select(Order).where(Order.id == order_id))
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # current user
    user = await session.scalar(select(User).where(User.email == current_user_email))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if not user.is_superuser and order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return {"status": order.status}
