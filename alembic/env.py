import asyncio
from logging.config import fileConfig
from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine

from app.db import Base
from app.models import *

# Alembic Config obyekti, bu .ini faylidagi qiymatlarga kirishni ta'minlaydi.
config = context.config

# Python logging uchun config faylini talqin qiladi.
# Bu qator loggerlarni sozlaydi.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# 'autogenerate' qo'llab-quvvatlash uchun modelning MetaData obyekti
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Migratsiyalarni 'offline' rejimida bajarish."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Migratsiyalarni 'online' rejimida bajarish."""
    connectable = AsyncEngine(
        engine_from_config(
            config.get_section(config.config_ini_section),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
