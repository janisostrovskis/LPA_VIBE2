"""SQLAlchemy implementation of OrganizationRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.organization_repository import OrganizationRepository
from app.domain.entities.organization import Organization
from app.infrastructure.database.models import OrganizationModel


def _model_to_entity(model: OrganizationModel) -> Organization:
    return Organization(
        id=model.id,
        legal_name=model.legal_name,
        registration_number=model.registration_number,
        vat_number=model.vat_number,
        address=model.address,
        contact_email=model.contact_email,
        contact_person_name=model.contact_person_name,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(org: Organization) -> OrganizationModel:
    return OrganizationModel(
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


class SqlaOrganizationRepository(OrganizationRepository):
    """Concrete OrganizationRepository backed by an AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, org: Organization) -> Organization:
        model = _entity_to_model(org)
        self._session.add(model)
        await self._session.flush()
        return _model_to_entity(model)

    async def get_by_id(self, org_id: UUID) -> Organization | None:
        result = await self._session.execute(
            select(OrganizationModel).where(OrganizationModel.id == org_id)
        )
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model is not None else None

    async def update(self, org: Organization) -> Organization:
        result = await self._session.execute(
            select(OrganizationModel).where(OrganizationModel.id == org.id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            from app.lib.errors import NotFoundError

            raise NotFoundError(message=f"Organization {org.id} not found")  # type: ignore[misc]
        model.legal_name = org.legal_name
        model.registration_number = org.registration_number
        model.vat_number = org.vat_number
        model.address = org.address
        model.contact_email = org.contact_email
        model.contact_person_name = org.contact_person_name
        model.updated_at = org.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, org_id: UUID) -> None:
        result = await self._session.execute(
            select(OrganizationModel).where(OrganizationModel.id == org_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            from app.lib.errors import NotFoundError

            raise NotFoundError(message=f"Organization {org_id} not found")  # type: ignore[misc]
        await self._session.delete(model)
        await self._session.flush()
