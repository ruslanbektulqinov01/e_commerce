from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db import get_async_session
from app.models.user import User
from app.schemas.user_schemas import UserOutSchema, UserUpdateSchema
from app.services.security import get_current_user
from app.controllers.user_controller import (
    get_user_by_id_logic,
    update_user_logic,
    delete_user_logic,
)

users_router = APIRouter(prefix="/users", tags=["Users"])


@users_router.get("/me", response_model=UserOutSchema)
async def get_me(
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    user = await session.scalar(select(User).where(User.email == current_user_email))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@users_router.get("/{user_id}", response_model=UserOutSchema)
async def get_user_by_id(
    user_id: int,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    current_user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    target_user = await get_user_by_id_logic(session, current_user, user_id)
    return target_user


@users_router.patch("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdateSchema,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    current_user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await update_user_logic(session, current_user, user_id, user_data)


@users_router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    current_user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return await delete_user_logic(session, current_user, user_id)
