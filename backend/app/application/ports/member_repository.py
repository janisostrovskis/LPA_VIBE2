"""Port: abstract repository for Member entities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.member import Member


class MemberRepository(ABC):
    """Abstract repository for Member persistence operations."""

    @abstractmethod
    async def create(self, member: Member) -> Member: ...

    @abstractmethod
    async def get_by_id(self, member_id: UUID) -> Member | None: ...

    @abstractmethod
    async def get_by_email(self, email: str) -> Member | None: ...

    @abstractmethod
    async def update(self, member: Member) -> Member: ...

    @abstractmethod
    async def delete(self, member_id: UUID) -> None: ...
