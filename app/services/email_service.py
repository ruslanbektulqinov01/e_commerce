from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from typing import List

from pydantic import EmailStr

from app.config import settings

conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_FROM_NAME=settings.MAIL_FROM_NAME,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
)


async def send_email(subject: str, email_to: List[EmailStr], body: str):
    message = MessageSchema(
        subject=subject,
        recipients=email_to,  # List of email recipients
        body=body,
        subtype=MessageType.html,
    )
    fm = FastMail(conf)
    await fm.send_message(message)


async def send_verification_email(email_to: EmailStr, verify_token: str):
    subject = "Verify your email"
    verification_link = f"http://localhost:8000/auth/verify-email?token={verify_token}"
    body = f"""
    <h1>Email Verification</h1>
    <p>Please click the link below to verify your email:</p>
    <a href="{verification_link}">Verify Email</a>
    """
    await send_email(subject, [email_to], body)


async def send_forgot_password_email(email_to: EmailStr, reset_token: str):
    subject = "Reset your password"
    reset_link = f"http://localhost:8000/auth/reset-password?token={reset_token}"
    body = f"""
    <h1>Reset Password</h1>
    <p>Please click the link below to reset your password:</p>
    <a href="{reset_link}">Reset Password</a>
    """
    await send_email(subject, [email_to], body)
