"""Alembic migration environment — async (psycopg3) configuration.

The database URL is read from the DATABASE_URL environment variable via
``app.infrastructure.config.env.get_settings()``.  The ``postgresql://``
scheme is rewritten to ``postgresql+psycopg://`` so the async driver is used
for both online migrations and autogenerate introspection.
"""

from __future__ import annotations

import asyncio
from logging.config import fileConfig

from alembic import context
from sqlalchemy.ext.asyncio import create_async_engine

from app.infrastructure.config.env import get_settings
from app.infrastructure.database.models import Base
from app.infrastructure.database.url import to_async_url

# ---------------------------------------------------------------------------
# Alembic Config object — gives access to the values in ``alembic.ini``.
# ---------------------------------------------------------------------------
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate support.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in *offline* mode (no live DB connection needed).

    This emits SQL to stdout so it can be reviewed or piped to a file.
    """
    url = to_async_url(get_settings().database_url)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async engine and run migrations in a single connection."""
    connectable = create_async_engine(
        to_async_url(get_settings().database_url),
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(_do_run_migrations)

    await connectable.dispose()


def _do_run_migrations(connection: object) -> None:
    context.configure(
        connection=connection,  # type: ignore[arg-type]
        target_metadata=target_metadata,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in *online* mode (connects to the live database)."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
