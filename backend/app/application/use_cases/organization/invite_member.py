"""Use case: invite an existing member to an organization."""

from __future__ import annotations

from uuid import UUID

from app.application.ports.email_sender import EmailSender
from app.application.ports.member_repository import MemberRepository
from app.domain.value_objects.email import Email
from app.lib.errors import DomainError, NotFoundError, ValidationError
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

    async def execute(self, org_id: UUID, email: str) -> Result[None, DomainError]:
        try:
            email_vo = Email.create(email)
        except ValueError as exc:
            return Err(ValidationError(message=str(exc)))

        member = await self._member_repo.get_by_email(email_vo.value)
        if member is None:
            return Err(NotFoundError(message="No member found with that email address."))

        await self._email_sender.send(
            to=member.email,
            subject="You have been invited to join an LPA organization",
            body=f"You have been invited to join an organization (ID: {org_id}). Log in to accept.",
        )
        return Ok(None)
