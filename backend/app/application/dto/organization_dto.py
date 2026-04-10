"""DTO for Organization — transport object between application and API layers."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.domain.entities.organization import Organization


class OrganizationDto(BaseModel):
    """Read model for an LPA organization."""

    id: UUID
    legal_name: str
    registration_number: str
    vat_number: str | None
    address: str
    contact_email: str
    contact_person_name: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, org: Organization) -> OrganizationDto:
        return cls(
            id=org.id,
            legal_name=org.legal_name,
            registration_number=org.registration_number,
            vat_number=org.vat_number,
            address=org.address,
            contact_email=org.contact_email,
            contact_person_name=org.contact_person_name,
            created_at=org.created_at,
            updated_at=org.updated_at,
        )


class OrganizationCreateBody(BaseModel):
    """Input for creating a new organization."""

    legal_name: str
    registration_number: str
    address: str
    contact_email: str
    contact_person_name: str
    vat_number: str | None = None


class InviteMemberBody(BaseModel):
    """Input for inviting a member to an organization."""

    email: str
