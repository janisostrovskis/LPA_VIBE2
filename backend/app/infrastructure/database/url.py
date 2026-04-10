"""Database URL rewriting for the psycopg3 async driver.

psycopg3's async engine requires ``postgresql+psycopg://`` instead of the
standard ``postgresql://`` scheme.  Centralised here so session.py and
alembic/env.py share the same logic.
"""

from __future__ import annotations

_SYNC_SCHEME = "postgresql://"
_ASYNC_SCHEME = "postgresql+psycopg://"


def to_async_url(url: str) -> str:
    """Rewrite *url* from ``postgresql://`` to ``postgresql+psycopg://``."""
    if url.startswith(_SYNC_SCHEME):
        return _ASYNC_SCHEME + url[len(_SYNC_SCHEME) :]
    return url
