"""Use case: invite an existing member to an organization."""

from __future__ import annotations

from uuid import UUID

from app.application.ports.email_sender import EmailSender
from app.application.ports.member_repository import MemberRepository
from app.domain.value_objects.email import Email
from app.domain.value_objects.role_name import RoleName
from app.lib.errors import DomainError, ForbiddenError, ValidationError
from app.lib.result import Err, Ok, Result


class InviteMember:
    """Send an invitation email to an existing member to join an organization."""

    def __init__(
        self,
        member_repo: MemberRepository,
        email_sender: EmailSender,
    ) -> None:
        self._member_repo = member_repo
        self._email_sender = email_sender

    async def execute(
        self, org_id: UUID, email: str, caller_id: UUID
    ) -> Result[None, DomainError]:
        try:
            email_vo = Email.create(email)
        except ValueError as exc:
            return Err(ValidationError(message=str(exc)))

        has_admin = await self._member_repo.has_org_role(caller_id, org_id, RoleName.ORG_ADMIN)
        if not has_admin:
            return Err(ForbiddenError(message="Only organization admins can invite members."))

        member = await self._member_repo.get_by_email(email_vo.value)
        if member is None:
            # Return Ok to prevent email enumeration: callers cannot distinguish
            # between "no account found" and "invite sent".
            return Ok(None)

        await self._email_sender.send(
            to=member.email,
            subject="You have been invited to join an LPA organization",
            body=f"You have been invited to join an organization (ID: {org_id}). Log in to accept.",
        )
        return Ok(None)
