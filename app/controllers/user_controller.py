from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from app.models.user import User
from app.schemas.user_schemas import UserUpdateSchema
from app.services.security import get_password_hash


async def get_user_by_id_logic(
    session: AsyncSession, current_user: User, user_id: int
) -> User:
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    target_user = await session.scalar(select(User).where(User.id == user_id))
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    return target_user


async def update_user_logic(
    session: AsyncSession, current_user: User, user_id: int, data: UserUpdateSchema
):
    if not current_user.is_superuser and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Forbidden")

    target_user = await session.scalar(select(User).where(User.id == user_id))
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    if data.email is not None:
        target_user.email = data.email
    if data.password is not None:
        target_user.hashed_password = get_password_hash(data.password)
    if data.is_active is not None:
        target_user.is_active = data.is_active
    if data.is_verified is not None:
        target_user.is_verified = data.is_verified
    if data.is_superuser is not None:
        target_user.is_superuser = data.is_superuser

    session.add(target_user)
    await session.commit()
    return {"message": "User updated successfully"}


async def delete_user_logic(session: AsyncSession, current_user: User, user_id: int):
    if not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Forbidden")

    target_user = await session.scalar(select(User).where(User.id == user_id))
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    await session.delete(target_user)
    await session.commit()
    return {"message": "User deleted successfully"}
