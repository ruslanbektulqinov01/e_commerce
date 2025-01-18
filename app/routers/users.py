from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.models.user import User
from app.schemas.user_schemas import UserOutSchema, UserUpdateSchema
from app.services.security import decode_access_token, get_password_hash
from app.services.security import get_current_user

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
    # Get current user
    current_user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Check permissions
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Get requested user
    user = await session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@users_router.patch("/{user_id}")
async def update_user(
    user_id: int,
    user_data: UserUpdateSchema,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # Get current user
    current_user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Check permissions
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Get target user
    user = await session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Update fields
    if user_data.email is not None:
        user.email = user_data.email
    if user_data.password is not None:
        user.hashed_password = get_password_hash(user_data.password)
    if user_data.is_active is not None:
        user.is_active = user_data.is_active
    if user_data.is_verified is not None:
        user.is_verified = user_data.is_verified
    if user_data.is_superuser is not None:
        user.is_superuser = user_data.is_superuser

    await session.commit()
    await session.refresh(user)
    return {"message": "User updated successfully"}


@users_router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user_email: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_async_session),
):
    # Get current user
    current_user = await session.scalar(
        select(User).where(User.email == current_user_email)
    )
    if not current_user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    # Check permissions
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Get target user
    user = await session.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(user)
    await session.commit()
    return {"message": "User deleted successfully"}
