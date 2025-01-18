from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine, async_sessionmaker, AsyncSession
from app.config import DATABASE_URL
from sqlalchemy.orm import declarative_base

Base = declarative_base()

# Asinxron SQLAlchemy engine yaratish
engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=True,  # ish jarayonini console da ko'rish uchun, xohlasa false qilinadi
)

# Asinxron session factory
async_session_maker = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# Dependency sifatida ishlatiladi
async def get_async_session() -> AsyncSession:
    async with async_session_maker() as session:
        yield session
