"""SQLAlchemy implementation of MagicLinkRepository."""

from __future__ import annotations

import uuid
from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.magic_link_repository import MagicLinkRepository
from app.infrastructure.database.models import MagicLinkTokenModel


class SqlaMagicLinkRepository(MagicLinkRepository):
    """Concrete MagicLinkRepository backed by an AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, token: str, user_id: UUID, expires_at: datetime) -> None:
        model = MagicLinkTokenModel(
            id=uuid.uuid4(),
            token=token,
            user_id=user_id,
            expires_at=expires_at,
            used=False,
        )
        self._session.add(model)
        await self._session.flush()

    async def consume(self, token: str) -> tuple[UUID, datetime] | None:
        """Return (user_id, expires_at) if token exists and is unused, else None.

        Marks the token as used atomically within the current transaction.
        """
        result = await self._session.execute(
            select(MagicLinkTokenModel).where(
                MagicLinkTokenModel.token == token,
                MagicLinkTokenModel.used.is_(False),
            )
        )
        model = result.scalar_one_or_none()
        if model is None:
            return None
        model.used = True
        await self._session.flush()
        return (model.user_id, model.expires_at)

    async def cleanup_expired(self) -> int:
        """Delete expired tokens. Return count deleted."""
        from sqlalchemy import func as sqla_func

        result = await self._session.execute(
            delete(MagicLinkTokenModel).where(
                MagicLinkTokenModel.expires_at < sqla_func.now()
            )
        )
        return int(result.rowcount)  # type: ignore[attr-defined]  # CursorResult at runtime
