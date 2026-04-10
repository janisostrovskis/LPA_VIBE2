"""Use case: export all personal data for a member (GDPR Article 20)."""

from __future__ import annotations

from uuid import UUID

from app.application.ports.member_repository import MemberRepository
from app.lib.errors import DomainError, NotFoundError
from app.lib.result import Err, Ok, Result


class ExportMemberData:
    """Return a dict of all stored personal data for the given member."""

    def __init__(self, member_repo: MemberRepository) -> None:
        self._member_repo = member_repo

    async def execute(self, member_id: UUID) -> Result[dict[str, object], DomainError]:
        member = await self._member_repo.get_by_id(member_id)
        if member is None:
            return Err(NotFoundError(message="Member not found."))

        return Ok(
            {
                "id": str(member.id),
                "email": member.email,
                "display_name": member.display_name,
                "preferred_locale": str(member.preferred_locale),
                "is_active": member.is_active,
                "created_at": member.created_at.isoformat(),
                "updated_at": member.updated_at.isoformat(),
            }
        )
