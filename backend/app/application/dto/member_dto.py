"""DTO for Member — transport object between application and API layers."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.entities.member import Member


class MemberDto(BaseModel):
    """Read model for a single LPA member."""

    id: UUID
    email: str
    display_name: str
    preferred_locale: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, member: Member) -> MemberDto:
        return cls(
            id=member.id,
            email=member.email,
            display_name=member.display_name,
            preferred_locale=str(member.preferred_locale),
            is_active=member.is_active,
            created_at=member.created_at,
            updated_at=member.updated_at,
        )


class MemberCreateDto(BaseModel):
    """Input DTO for registering a new member."""

    email: str
    display_name: str
    password: str
    preferred_locale: str = "lv"
