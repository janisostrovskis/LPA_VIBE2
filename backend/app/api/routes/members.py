"""FastAPI router for member profile endpoints."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.api.dependencies import get_member_repo
from app.api.middleware.auth import require_member_id
from app.api.routes._errors import result_to_response
from app.application.dto.member_dto import MemberDto
from app.application.ports.member_repository import MemberRepository
from app.application.use_cases.member.export_data import ExportMemberData
from app.application.use_cases.member.update_profile import UpdateProfile
from app.lib.errors import NotFoundError
from app.lib.result import Err, Ok

router = APIRouter(prefix="/api/members", tags=["members"])


class ProfileUpdateBody(BaseModel):
    """Partial update payload for a member's profile."""

    display_name: str | None = None
    preferred_locale: str | None = None


@router.get("/me", response_model=MemberDto)
async def get_me(
    member_id: Annotated[UUID, Depends(require_member_id)],
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
) -> MemberDto:
    """Return the authenticated member's profile."""
    member = await member_repo.get_by_id(member_id)
    if member is None:
        result: Ok[MemberDto] | Err[NotFoundError] = Err(
            NotFoundError(message="Member not found.")
        )
    else:
        result = Ok(MemberDto.from_entity(member))
    return result_to_response(result)


@router.patch("/me", response_model=MemberDto)
async def update_me(
    body: ProfileUpdateBody,
    member_id: Annotated[UUID, Depends(require_member_id)],
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
) -> MemberDto:
    """Update the authenticated member's display name and/or preferred locale."""
    use_case = UpdateProfile(member_repo=member_repo)
    result = await use_case.execute(
        member_id=member_id,
        display_name=body.display_name,
        preferred_locale=body.preferred_locale,
    )
    return result_to_response(result)


@router.get("/me/export")
async def export_me(
    member_id: Annotated[UUID, Depends(require_member_id)],
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
) -> dict[str, object]:
    """Export all personal data for the authenticated member (GDPR Article 20)."""
    use_case = ExportMemberData(member_repo=member_repo)
    result = await use_case.execute(member_id)
    return result_to_response(result)
