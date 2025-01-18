from fastapi import APIRouter, Depends, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_async_session
from app.schemas.auth_schemas import (
    UserRegisterSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    TokenSchema,
)
from app.controllers.auth_controller import (
    register_user_logic,
    login_user_logic,
    verify_email_logic,
    forgot_password_logic,
    reset_password_logic,
)

auth_router = APIRouter(prefix="/auth", tags=["Auth"])


@auth_router.post("/register", response_model=TokenSchema)
async def register_user(
    user_data: UserRegisterSchema, session: AsyncSession = Depends(get_async_session)
):
    access_token = await register_user_logic(session, user_data)
    return TokenSchema(access_token=access_token)


@auth_router.post("/login", response_model=TokenSchema)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_async_session),
):
    email = form_data.username
    password = form_data.password
    access_token = await login_user_logic(session, email, password)
    return TokenSchema(access_token=access_token)


@auth_router.get("/verify-email")
async def verify_email(
    token: str = Query(...), session: AsyncSession = Depends(get_async_session)
):
    return await verify_email_logic(session, token)


@auth_router.post("/forgot-password")
async def forgot_password(
    data: ForgotPasswordSchema, session: AsyncSession = Depends(get_async_session)
):
    return await forgot_password_logic(session, data.email)


@auth_router.post("/reset-password")
async def reset_password(
    data: ResetPasswordSchema, session: AsyncSession = Depends(get_async_session)
):
    return await reset_password_logic(session, data.token, data.new_password)
