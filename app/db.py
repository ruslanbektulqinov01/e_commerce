from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from app.config import DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME, USE_SQLITE_IN_MEMORY

Base = declarative_base()

if USE_SQLITE_IN_MEMORY:
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
else:
    # PostgreSQL misoli
    DATABASE_URL = (
        f"postgresql+asyncpg://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    )

engine = create_async_engine(DATABASE_URL, echo=False)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False)


async def get_async_session() -> AsyncSession:
    async with SessionLocal() as session:
        yield session
