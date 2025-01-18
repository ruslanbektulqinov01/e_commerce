from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_async_session
from app.models.user import User
from app.schemas.order_schemas import OrderCreateSchema, OrderOutSchema
from app.services.security import get_current_user
from app.controllers.order_controller import (
    create_order_logic,
    get_order_logic,
    get_all_orders_logic,
    get_customer_orders_logic,
    get_order_status_logic,
)

orders_router = APIRouter(prefix="/orders", tags=["Orders"])


@orders_router.post("/", response_model=OrderOutSchema)
async def create_order(
    order_data: OrderCreateSchema,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # current user
    current_user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    new_order = await create_order_logic(session, current_user.id, order_data)
    return new_order


@orders_router.get("/{order_id}", response_model=OrderOutSchema)
async def get_order(
    order_id: int,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    current_user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await get_order_logic(session, current_user, order_id)


@orders_router.get("/", response_model=List[OrderOutSchema])
async def get_all_orders(
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # Faqat admin
    current_user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await get_all_orders_logic(session, current_user)


@orders_router.get("/customer/{customer_id}", response_model=List[OrderOutSchema])
async def get_customer_orders(
    customer_id: int,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    current_user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return await get_customer_orders_logic(session, current_user, customer_id)


@orders_router.get("/{order_id}/status")
async def get_order_status(
    order_id: int,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    current_user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await get_order_status_logic(session, current_user, order_id)
