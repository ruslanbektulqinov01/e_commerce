from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from typing import List
from app.config import (
    MAIL_USERNAME,
    MAIL_PASSWORD,
    MAIL_FROM,
    MAIL_PORT,
    MAIL_SERVER,
    MAIL_FROM_NAME,
    MAIL_STARTTLS,
    MAIL_SSL_TLS,
)

conf = ConnectionConfig(
    MAIL_USERNAME=MAIL_USERNAME,
    MAIL_PASSWORD=MAIL_PASSWORD,
    MAIL_FROM=MAIL_FROM,
    MAIL_PORT=MAIL_PORT,
    MAIL_SERVER=MAIL_SERVER,
    MAIL_FROM_NAME=MAIL_FROM_NAME,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    MAIL_STARTTLS=MAIL_STARTTLS,
    MAIL_SSL_TLS=MAIL_SSL_TLS,
)


async def send_email(subject: str, email_to: List[str], body: str):
    message = MessageSchema(
        subject=subject, recipients=email_to, body=body, subtype=MessageType.html
    )
    fm = FastMail(conf)
    await fm.send_message(message)


async def send_verification_email(email_to: str, verify_token: str):
    subject = "Emailingizni tasdiqlang"
    verification_link = f"http://localhost:8000/auth/verify-email?token={verify_token}"
    body = f"""
    <h1>Emailni tasdiqlash</h1>
    <p>Iltimos, emailingizni tasdiqlash uchun quyidagi havolani bosing:</p>
    <a href="{verification_link}">Emailni tasdiqlash</a>
    """
    await send_email(subject, [email_to], body)


async def send_forgot_password_email(email_to: str, reset_token: str):
    subject = "Parolingizni tiklang"
    reset_link = f"http://localhost:8000/auth/reset-password?token={reset_token}"
    body = f"""
    <h1>Parolni tiklash</h1>
    <p>Iltimos, parolingizni tiklash uchun quyidagi havolani bosing:</p>
    <a href="{reset_link}">Parolni tiklash</a>
    """
    await send_email(subject, [email_to], body)
