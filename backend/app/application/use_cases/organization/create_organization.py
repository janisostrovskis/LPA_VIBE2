"""Use case: create a new LPA organization."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from app.application.ports.organization_repository import OrganizationRepository
from app.domain.entities.organization import Organization
from app.domain.value_objects.email import Email
from app.lib.errors import DomainError, ValidationError
from app.lib.result import Err, Ok, Result


class CreateOrganization:
    """Register a new organization (studio or association) with LPA."""

    def __init__(self, org_repo: OrganizationRepository) -> None:
        self._org_repo = org_repo

    async def execute(
        self,
        legal_name: str,
        registration_number: str,
        address: str,
        contact_email: str,
        contact_person_name: str,
        vat_number: str | None = None,
    ) -> Result[Organization, DomainError]:
        try:
            email_vo = Email.create(contact_email)
        except ValueError as exc:
            return Err(ValidationError(message=str(exc)))

        now = datetime.now(tz=UTC)
        org = Organization(
            id=uuid4(),
            legal_name=legal_name,
            registration_number=registration_number,
            vat_number=vat_number,
            address=address,
            contact_email=email_vo.value,
            contact_person_name=contact_person_name,
            created_at=now,
            updated_at=now,
        )
        created = await self._org_repo.create(org)
        return Ok(created)
