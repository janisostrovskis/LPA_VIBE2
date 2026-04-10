"""FastAPI router for organization endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from app.api.dependencies import get_email_sender, get_member_repo, get_org_repo
from app.api.middleware.auth import require_member_id
from app.api.routes._errors import result_to_response
from app.application.dto.organization_dto import (
    InviteMemberBody,
    OrganizationCreateBody,
    OrganizationDto,
)
from app.application.ports.email_sender import EmailSender
from app.application.ports.member_repository import MemberRepository
from app.application.ports.organization_repository import OrganizationRepository
from app.application.use_cases.organization.create_organization import CreateOrganization
from app.application.use_cases.organization.invite_member import InviteMember

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=OrganizationDto)
async def create_organization(
    body: OrganizationCreateBody,
    _member_id: Annotated[UUID, Depends(require_member_id)],
    org_repo: Annotated[OrganizationRepository, Depends(get_org_repo)],
) -> OrganizationDto:
    """Create a new LPA organization. Caller must be authenticated."""
    use_case = CreateOrganization(org_repo=org_repo)
    result = await use_case.execute(
        legal_name=body.legal_name,
        registration_number=body.registration_number,
        address=body.address,
        contact_email=body.contact_email,
        contact_person_name=body.contact_person_name,
        vat_number=body.vat_number,
    )
    org = result_to_response(result, success_status=status.HTTP_201_CREATED)
    return OrganizationDto.from_entity(org)


@router.post("/{org_id}/invite", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def invite_member(
    org_id: UUID,
    body: InviteMemberBody,
    _member_id: Annotated[UUID, Depends(require_member_id)],
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
) -> None:
    """Invite an existing member to the specified organization."""
    use_case = InviteMember(member_repo=member_repo, email_sender=email_sender)
    result = await use_case.execute(org_id=org_id, email=body.email)
    result_to_response(result, success_status=status.HTTP_204_NO_CONTENT)
