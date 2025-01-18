from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.auth_schemas import UserRegisterSchema
from app.services.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.services.email_service import (
    send_verification_email,
    send_forgot_password_email,
)


async def register_user_logic(session: AsyncSession, user_data: UserRegisterSchema):
    # 1) Email band emasligini tekshirish
    existing = await session.execute(select(User).where(User.email == user_data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )
    # 2) Yangi user
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        is_superuser=user_data.is_superuser,
        is_active=True,
        is_verified=False,
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # 3) Email verify token
    verify_token = create_access_token({"sub": new_user.email}, expires_delta=60)
    await send_verification_email(new_user.email, verify_token)

    # Access token
    access_token = create_access_token({"sub": new_user.email})
    return access_token


async def login_user_logic(session: AsyncSession, email: str, password: str):
    # userni topish
    user = await session.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User not verified")

    access_token = create_access_token({"sub": user.email})
    return access_token


async def verify_email_logic(session: AsyncSession, token: str):
    from jose import jwt
    from app.config import JWT_SECRET, JWT_ALGORITHM

    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = await session.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.is_verified = True
    session.add(user)
    await session.commit()
    return {"message": "Email verified successfully"}


async def forgot_password_logic(session: AsyncSession, email: str):
    user = await session.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    reset_token = create_access_token({"sub": user.email}, expires_delta=60)
    await send_forgot_password_email(user.email, reset_token)
    return {"message": "Reset token sent"}


async def reset_password_logic(session: AsyncSession, token: str, new_password: str):
    from jose import jwt
    from app.config import JWT_SECRET, JWT_ALGORITHM

    payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    user = await session.scalar(select(User).where(User.email == email))
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.hashed_password = get_password_hash(new_password)
    session.add(user)
    await session.commit()
    return {"message": "Password has been reset successfully"}
