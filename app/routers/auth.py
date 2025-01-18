from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.models.user import User
from app.schemas.auth_schemas import (
    UserRegisterSchema,
    UserLoginSchema,
    ResendVerificationSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    TokenSchema,
)
from app.services.security import (
    get_password_hash,
    verify_password,
    create_access_token,
)
from app.services.email_service import (
    send_verification_email,
    send_forgot_password_email,
)
from jose import jwt
from app.config import settings

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register/", response_model=TokenSchema)
async def register_user(
    user_data: UserRegisterSchema, session: AsyncSession = Depends(get_async_session)
):
    # 1) Email bandligini tekshirish
    existing_user = await session.execute(
        select(User).where(User.email == user_data.email)
    )
    if existing_user.first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered"
        )

    # 2) Parolni xeshlash
    hashed_password = get_password_hash(user_data.password)

    # 3) Yangi foydalanuvchini yaratish
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

    # 4) Email verifikatsiya tokeni
    verify_token = create_access_token({"sub": new_user.email}, expires_delta=60 * 60)

    # 5) Email yuborish
    await send_verification_email(new_user.email, verify_token)

    # 6) Ro‘yxatdan o‘tgan userga access_token qaytarish (ixtiyoriy)
    access_token = create_access_token({"sub": new_user.email})
    return TokenSchema(access_token=access_token)


@auth_router.post("/login", response_model=TokenSchema)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    # Bu yerda `form_data.username` -> email sifatida qabul qilinadi
    email = form_data.username
    password = form_data.password

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    if not user.is_verified:
        raise HTTPException(status_code=403, detail="User not verified")

    # Token yaratish
    access_token = create_access_token({"sub": user.email})
    return TokenSchema(access_token=access_token)


@auth_router.get("/verify-email/")
async def verify_email(
    token: str = Query(...), session: AsyncSession = Depends(get_async_session)
):
    payload = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Foydalanuvchini topish
    result = await session.execute(select(User).where(User.email == email))

    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.is_verified = True
    session.add(user)
    await session.commit()
    return {"message": "Email verified successfully"}


@auth_router.get("/verify-email/")
async def verify_email(
    token: str = Query(...), session: AsyncSession = Depends(get_async_session)
):
    payload = jwt.decode(
        token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    # Retrieve the user
    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    user.is_verified = True
    session.add(user)
    await session.commit()
    return {"message": "Email verified successfully"}


@auth_router.post("/forgot-password/")
async def forgot_password(
    data: ForgotPasswordSchema, session: AsyncSession = Depends(get_async_session)
):
    result = await session.execute(select(User).where(User.email == data.email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")

    reset_token = create_access_token({"sub": user.email}, expires_delta=60 * 60)
    await send_forgot_password_email(user.email, reset_token)
    return {"message": "Password reset email sent"}


@auth_router.post("/reset-password/")
async def reset_password(
    data: ResetPasswordSchema, session: AsyncSession = Depends(get_async_session)
):
    payload = jwt.decode(
        data.token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
    )
    email = payload.get("sub")
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")

    result = await session.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=400, detail="User not found")
    user.hashed_password = get_password_hash(data.new_password)
    session.add(user)
    await session.commit()
    return {"message": "Password has been reset successfully"}
