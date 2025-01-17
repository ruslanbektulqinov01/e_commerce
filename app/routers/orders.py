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
from app.services.security import decode_access_token

orders_router = APIRouter(prefix="/api/orders", tags=["Orders"])

async def get_current_user(token: str = Depends()):
    payload = decode_access_token(token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return payload.get("sub")  # user email

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
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session)
):
    # userni topish
    user = await session.scalar(select(User).where(User.email == current_user_email))
    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Yangi buyurtma
    new_order = Order(user_id=user.id, status="pending")
    session.add(new_order)
    await session.commit()
    await session.refresh(new_order)

    # itemlarni yaratish
    for item in order_data.items:
        # product bor-yo‘qligini tekshirish
        product = await session.scalar(select(Product).where(Product.id == item.product_id))
        if not product:
            raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=product.id,
            quantity=item.quantity,
            price=item.price
        )
        session.add(order_item)

    await session.commit()
    # itemlarni olib kelish
    items = await session.scalars(select(OrderItem).where(OrderItem.order_id == new_order.id))
    new_order.items = items.all()

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
