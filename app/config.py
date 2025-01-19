import os
from dotenv import load_dotenv
from pydantic_settings import SettingsConfigDict

load_dotenv()  # .env faylidan environment variable-larni yuklab olamiz

# Bu yerda eng zarur sozlamalar
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "test_db")
DB_USER = os.getenv("DB_USER", "test_user")
DB_PASS = os.getenv("DB_PASS", "test_pass")


JWT_SECRET = os.getenv("JWT_SECRET", "SUPER_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

MAIL_USERNAME = os.getenv("MAIL_USERNAME", "example@gmail.com")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD", "app-password")
MAIL_FROM = os.getenv("MAIL_FROM", "example@gmail.com")
MAIL_PORT = int(os.getenv("MAIL_PORT", "587"))
MAIL_SERVER = os.getenv("MAIL_SERVER", "smtp.gmail.com")
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "FastAPI Project")
MAIL_STARTTLS = True
MAIL_SSL_TLS = False
model_config = SettingsConfigDict(case_sensitive=True)
