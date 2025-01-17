from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.models.user import User
from app.schemas.auth_schemas import (
    UserRegisterSchema, UserLoginSchema,
    ResendVerificationSchema, ForgotPasswordSchema,
    ResetPasswordSchema, TokenSchema
)
from app.services.security import get_password_hash, verify_password, create_access_token
from app.services.email_service import send_verification_email, send_forgot_password_email
from jose import jwt
from app.config import settings

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register/", response_model=TokenSchema)
async def register_user(
        user_data: UserRegisterSchema,
        session: AsyncSession = Depends(get_async_session)
):
    # Email mavjud emasligini tekshiramiz
    existing_user = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    # Parolni xeshlash
    hashed_password = get_password_hash(user_data.password)

    # Foydalanuvchi yaratish
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        is_active=True,
        is_verified=False,
        is_superuser=False
    )
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    # Email verify token yaratish
    verify_token = create_access_token({"sub": new_user.email}, expires_delta=60 * 60)  # 1 soatga

    # Email yuborish (async)
    await send_verification_email(new_user.email, verify_token)

    # Dastlabki login token qaytaramiz (ixtiyoriy, yoki 'None' qilishingiz mumkin)
    access_token = create_access_token({"sub": new_user.email})
    return TokenSchema(access_token=access_token)


@auth_router.post("/login/", response_model=TokenSchema)
async def login_user(
        user_data: UserLoginSchema,
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    user_row = result.first()
    if not user_row:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    user = User(**dict(user_row))

    if not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User email is not verified")

    access_token = create_access_token({"sub": user.email})
    return TokenSchema(access_token=access_token)


@auth_router.get("/verify-email/")
async def verify_email(token: str = Query(...), session: AsyncSession = Depends(get_async_session)):
    payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Foydalanuvchini topish
    result = await session.execute(
        select(User).where(User.email == email)
    )

    user_row = result.first()
    if not user_row:
        raise HTTPException(status_code=400, detail="User not found")

    user = User(**dict(user_row))
    user.is_verified = True
    session.add(user)
    await session.commit()
    return {"message": "Email verified successfully"}


@auth_router.post("/resend-verification/")
async def resend_verification(
        data: ResendVerificationSchema,
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(User).where(User.email == data.email)
    )
    user_row = result.first()
    if not user_row:
        raise HTTPException(status_code=400, detail="User not found")

    user = User(**dict(user_row))
    if user.is_verified:
        raise HTTPException(status_code=400, detail="Email already verified")

    verify_token = create_access_token({"sub": user.email}, expires_delta=60 * 60)
    await send_verification_email(user.email, verify_token)
    return {"message": "Verification email resent"}


@auth_router.post("/forgot-password/")
async def forgot_password(
        data: ForgotPasswordSchema,
        session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(
        select(User).where(User.email == data.email)
    )
    user_row = result.first()
    if not user_row:
        raise HTTPException(status_code=400, detail="User not found")

    user = User(**dict(user_row))
    reset_token = create_access_token({"sub": user.email}, expires_delta=60 * 60)
    await send_forgot_password_email(user.email, reset_token)
    return {"message": "Password reset email sent"}


@auth_router.post("/reset-password/")
async def reset_password(
        data: ResetPasswordSchema,
        session: AsyncSession = Depends(get_async_session)
):
    payload = jwt.decode(data.token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    result = await session.execute(
        select(User).where(User.email == email)
    )
    user_row = result.first()
    if not user_row:
        raise HTTPException(status_code=400, detail="User not found")

    user = User(**dict(user_row))
    user.hashed_password = get_password_hash(data.new_password)
    session.add(user)
    await session.commit()
    return {"message": "Password has been reset successfully"}
