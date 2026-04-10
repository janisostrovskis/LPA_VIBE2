"""Async SQLAlchemy session factory.

Engine and session-maker are created lazily on first use so that importing
this module does not trigger Settings parsing or network I/O at import time.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.infrastructure.config.env import get_settings
from app.infrastructure.database.url import to_async_url


@lru_cache(maxsize=1)
def _get_engine() -> AsyncEngine:
    return create_async_engine(
        to_async_url(get_settings().database_url),
        echo=False,
        future=True,
    )


@lru_cache(maxsize=1)
def _get_session_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=_get_engine(),
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
        autocommit=False,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields a database session per request.

    The session is committed on clean exit and rolled back on exception.
    """
    async with _get_session_factory()() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
