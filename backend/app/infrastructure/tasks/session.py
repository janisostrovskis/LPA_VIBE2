"""Worker-side async SQLAlchemy session factory.

Provides an independent engine and sessionmaker for Celery tasks.
Tasks must never share the FastAPI request-scoped session; this factory
creates a separate connection pool that the worker fully owns.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.config.env import get_settings
from app.infrastructure.database.url import to_async_url

_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def build_worker_sessionmaker() -> async_sessionmaker[AsyncSession]:
    """Return (creating on first call) an async sessionmaker for worker tasks.

    Uses the same DATABASE_URL env var as the request-scoped session but
    creates a separate engine so task DB connections are fully independent
    of the FastAPI connection pool.  Raises ValidationError at worker startup
    if DATABASE_URL is missing or malformed (fail-loudly).
    """
    global _sessionmaker  # noqa: PLW0603
    if _sessionmaker is not None:
        return _sessionmaker

    database_url = get_settings().database_url
    engine = create_async_engine(
        to_async_url(database_url),
        echo=False,
        future=True,
    )
    _sessionmaker = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )
    return _sessionmaker
