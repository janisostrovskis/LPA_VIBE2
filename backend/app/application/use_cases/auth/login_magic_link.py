"""Use cases: request and verify a magic-link authentication token."""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta

from app.application.dto.auth_dto import MagicLinkRequest, MagicLinkVerifyRequest, TokenResponse
from app.application.ports.auth_service import AuthService
from app.application.ports.email_sender import EmailSender
from app.application.ports.magic_link_repository import MagicLinkRepository
from app.application.ports.member_repository import MemberRepository
from app.domain.errors.auth_error import InvalidCredentialsError, MagicLinkExpiredError
from app.domain.rules.auth_rules import is_magic_link_expired
from app.lib.errors import DomainError
from app.lib.result import Err, Ok, Result

_MAGIC_LINK_TTL_MINUTES = 15


class RequestMagicLink:
    """Generate and email a one-time magic-link token to an existing member."""

    def __init__(
        self,
        member_repo: MemberRepository,
        magic_link_repo: MagicLinkRepository,
        email_sender: EmailSender,
    ) -> None:
        self._member_repo = member_repo
        self._magic_link_repo = magic_link_repo
        self._email_sender = email_sender

    async def execute(self, dto: MagicLinkRequest) -> Result[None, DomainError]:
        member = await self._member_repo.get_by_email(dto.email.strip().lower())
        if member is None:
            # Return Ok to prevent email enumeration: callers cannot distinguish
            # between "account not found" and "email sent".
            return Ok(None)

        token = secrets.token_urlsafe(32)
        expires_at = datetime.now(tz=UTC) + timedelta(minutes=_MAGIC_LINK_TTL_MINUTES)
        await self._magic_link_repo.create(token, member.id, expires_at)

        await self._email_sender.send(
            to=member.email,
            subject="Your LPA login link",
            body=(
                f"Use this token to log in: {token}\n\n"
                f"It expires in {_MAGIC_LINK_TTL_MINUTES} minutes."
            ),
        )
        return Ok(None)


class VerifyMagicLink:
    """Consume a magic-link token and issue a JWT on success."""

    def __init__(
        self,
        magic_link_repo: MagicLinkRepository,
        auth_service: AuthService,
        member_repo: MemberRepository,
    ) -> None:
        self._magic_link_repo = magic_link_repo
        self._auth_service = auth_service
        self._member_repo = member_repo

    async def execute(self, dto: MagicLinkVerifyRequest) -> Result[TokenResponse, DomainError]:
        result = await self._magic_link_repo.consume(dto.token)
        if result is None:
            return Err(InvalidCredentialsError(message="Invalid or already-used magic link."))

        member_id, expires_at = result
        if is_magic_link_expired(expires_at):
            return Err(MagicLinkExpiredError(message="Magic link has expired."))

        member = await self._member_repo.get_by_id(member_id)
        if member is None or not member.is_active:
            return Err(InvalidCredentialsError(message="Invalid or already-used magic link."))

        token = self._auth_service.issue_token(str(member_id))
        return Ok(TokenResponse(access_token=token))
