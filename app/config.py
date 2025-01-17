import os
from pydantic import BaseSettings
from dotenv import load_dotenv

load_dotenv()  # .env faylidan environment variable-larni yuklab olamiz

class Settings(BaseSettings):
    DB_HOST: str = os.getenv("DB_HOST")
    DB_PORT: str = os.getenv("DB_PORT")
    DB_NAME: str = os.getenv("DB_NAME")
    DB_USER: str = os.getenv("DB_USER")
    DB_PASS: str = os.getenv("DB_PASS")

    JWT_SECRET: str = os.getenv("JWT_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))

    MAIL_USERNAME: str = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: str = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: str = os.getenv("MAIL_FROM")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", 587))
    MAIL_SERVER: str = os.getenv("MAIL_SERVER")
    MAIL_FROM_NAME: str = os.getenv("MAIL_FROM_NAME", "FastAPI Project")
    MAIL_STARTTLS: bool = bool(os.getenv("MAIL_STARTTLS", True))
    MAIL_SSL_TLS: bool = bool(os.getenv("MAIL_SSL_TLS", False))

    class Config:
        case_sensitive = True


settings = Settings()

# PostgreSQL uchun DSN (Database URL):
DATABASE_URL = f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASS}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
