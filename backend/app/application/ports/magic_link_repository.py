"""Port: abstract repository for MagicLinkToken operations."""

from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class MagicLinkRepository(ABC):
    """Abstract repository for single-use magic link tokens."""

    @abstractmethod
    async def create(
        self,
        token: str,
        user_id: UUID,
        expires_at: datetime,
        purpose: str = "login",
    ) -> None: ...

    @abstractmethod
    async def consume(
        self,
        token: str,
        purpose: str = "login",
    ) -> tuple[UUID, datetime] | None:
        """Return (user_id, expires_at) if token exists, is unused, and matches
        the given purpose, else None.

        Marks the token as used atomically.  Filtering by purpose prevents an
        activation token from being accepted as a login token and vice versa.
        """
        ...

    @abstractmethod
    async def invalidate_unused_for_user(
        self, user_id: UUID, purpose: str = "login"
    ) -> int:
        """Mark all unused tokens for this (user_id, purpose) as used.

        Returns count invalidated. Used when issuing a fresh token to ensure
        prior tokens cannot be redeemed after superseding.
        """
        ...

    @abstractmethod
    async def cleanup_expired(self) -> int:
        """Delete expired tokens. Return count deleted."""
        ...
