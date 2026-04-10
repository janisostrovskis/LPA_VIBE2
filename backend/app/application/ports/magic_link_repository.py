"""Port: abstract repository for MagicLinkToken operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class MagicLinkRepository(ABC):
    """Abstract repository for single-use magic link tokens."""

    @abstractmethod
    async def create(self, token: str, user_id: UUID, expires_at: datetime) -> None: ...

    @abstractmethod
    async def consume(self, token: str) -> tuple[UUID, datetime] | None:
        """Return (user_id, expires_at) if token exists and is unused, else None.

        Marks the token as used atomically.
        """
        ...

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Delete expired tokens. Return count deleted."""
        ...
