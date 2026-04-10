"""Use case: update a member's profile fields."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID

from app.application.dto.member_dto import MemberDto
from app.application.ports.member_repository import MemberRepository
from app.domain.value_objects.locale import Locale
from app.lib.errors import DomainError, NotFoundError, ValidationError
from app.lib.result import Err, Ok, Result


class UpdateProfile:
    """Update display_name and/or preferred_locale for an existing member."""

    def __init__(self, member_repo: MemberRepository) -> None:
        self._member_repo = member_repo

    async def execute(
        self,
        member_id: UUID,
        display_name: str | None = None,
        preferred_locale: str | None = None,
    ) -> Result[MemberDto, DomainError]:
        member = await self._member_repo.get_by_id(member_id)
        if member is None:
            return Err(NotFoundError(message="Member not found."))

        if display_name is not None:
            member.display_name = display_name

        if preferred_locale is not None:
            try:
                member.preferred_locale = Locale(preferred_locale)
            except ValueError:
                return Err(ValidationError(message=f"Unsupported locale: {preferred_locale!r}"))

        member.updated_at = datetime.now(tz=UTC)
        updated = await self._member_repo.update(member)
        return Ok(MemberDto.from_entity(updated))
