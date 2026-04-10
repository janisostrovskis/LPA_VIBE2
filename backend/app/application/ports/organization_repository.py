"""Port: abstract repository for Organization entities."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from app.domain.entities.organization import Organization


class OrganizationRepository(ABC):
    """Abstract repository for Organization persistence operations."""

    @abstractmethod
    async def create(self, org: Organization) -> Organization: ...

    @abstractmethod
    async def get_by_id(self, org_id: UUID) -> Organization | None: ...

    @abstractmethod
    async def update(self, org: Organization) -> Organization: ...

    @abstractmethod
    async def delete(self, org_id: UUID) -> None: ...
