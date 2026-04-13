"""Use cases: activate account via email link, and resend activation email."""

from __future__ import annotations

from datetime import UTC, datetime

from app.application.dto.auth_dto import TokenResponse
from app.application.ports.auth_service import AuthService
from app.application.ports.email_sender import EmailSender
from app.application.ports.magic_link_repository import MagicLinkRepository
from app.application.ports.member_repository import MemberRepository
from app.application.services.activation_email import send_activation_email
from app.domain.errors.auth_error import ActivationTokenInvalidError
from app.domain.rules.auth_rules import is_magic_link_expired
from app.domain.value_objects.magic_link_purpose import MagicLinkPurpose
from app.lib.errors import DomainError
from app.lib.result import Err, Ok, Result


class ActivateAccount:
    """Consume an activation token, mark the member active, and issue a JWT."""

    def __init__(
        self,
        member_repo: MemberRepository,
        magic_link_repo: MagicLinkRepository,
        auth_service: AuthService,
    ) -> None:
        self._member_repo = member_repo
        self._magic_link_repo = magic_link_repo
        self._auth_service = auth_service

    async def execute(self, token: str) -> Result[TokenResponse, DomainError]:
        consumed = await self._magic_link_repo.consume(
            token, purpose=MagicLinkPurpose.ACTIVATION
        )
        if consumed is None:
            return Err(
                ActivationTokenInvalidError(
                    message="Invalid or already-used activation link."
                )
            )

        member_id, expires_at = consumed
        if is_magic_link_expired(expires_at):
            return Err(ActivationTokenInvalidError(message="Activation link has expired."))

        member = await self._member_repo.get_by_id(member_id)
        if member is None:
            return Err(
                ActivationTokenInvalidError(
                    message="Invalid or already-used activation link."
                )
            )

        if not member.is_active:
            member.is_active = True
            member.updated_at = datetime.now(tz=UTC)
            await self._member_repo.update(member)

        jwt = self._auth_service.issue_token(str(member_id))
        return Ok(TokenResponse(access_token=jwt))


class ResendActivation:
    """Send a fresh activation email if the account exists and is not yet activated.

    Always returns Ok(None) regardless — prevents email enumeration.
    """

    def __init__(
        self,
        member_repo: MemberRepository,
        magic_link_repo: MagicLinkRepository,
        email_sender: EmailSender,
        frontend_url: str,
    ) -> None:
        self._member_repo = member_repo
        self._magic_link_repo = magic_link_repo
        self._email_sender = email_sender
        self._frontend_url = frontend_url

    async def execute(self, email: str) -> Result[None, DomainError]:
        # SECURITY NOTE (Phase 02 post-close finding, MEDIUM, accepted):
        # This handler is not constant-time across the "exists & inactive"
        # vs "missing / already active" branches. The slow path performs a
        # token invalidate + insert + email send; the fast path does none
        # of those. A precise timing-oracle attacker can distinguish.
        # Mitigation: per-IP rate limiting at the edge (Phase 09), plus
        # moving the slow-path work onto a background worker with its own
        # DB session once a task queue (Celery/RQ) lands. A simple
        # asyncio.create_task does not work here because the SQLAlchemy
        # session is request-scoped and closes when the handler returns.
        member = await self._member_repo.get_by_email(email.strip().lower())
        if member is None or member.is_active:
            return Ok(None)

        await send_activation_email(
            magic_link_repo=self._magic_link_repo,
            email_sender=self._email_sender,
            user_id=member.id,
            email=member.email,
            locale=str(member.preferred_locale),
            frontend_url=self._frontend_url,
            welcome=False,
        )
        return Ok(None)
