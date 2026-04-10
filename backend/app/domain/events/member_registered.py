"""Domain event emitted when a new member completes registration."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass(frozen=True)
class MemberRegistered:
    member_id: UUID
    email: str
    registered_at: datetime
