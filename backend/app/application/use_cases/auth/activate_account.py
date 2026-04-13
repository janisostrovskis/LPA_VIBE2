"""Use cases: activate account via email link, and resend activation email."""

from __future__ import annotations

from datetime import UTC, datetime

from app.application.dto.auth_dto import TokenResponse
from app.application.ports.auth_service import AuthService
from app.application.ports.email_queue import EmailQueue
from app.application.ports.magic_link_repository import MagicLinkRepository
from app.application.ports.member_repository import MemberRepository
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
    The activation email is enqueued to a Celery worker so the expensive DB
    writes and SMTP round-trip happen off the request path. The slow branch
    still pays a microsecond-level Redis RPUSH that the fast branch skips;
    this residual µs-scale asymmetry is not a usable oracle when combined
    with the per-IP rate limits on /resend-activation (3/minute, 10/hour).
    """

    def __init__(
        self,
        member_repo: MemberRepository,
        email_queue: EmailQueue,
        frontend_url: str,
    ) -> None:
        self._member_repo = member_repo
        self._email_queue = email_queue
        self._frontend_url = frontend_url

    async def execute(self, email: str) -> Result[None, DomainError]:
        member = await self._member_repo.get_by_email(email.strip().lower())
        if member is None or member.is_active:
            return Ok(None)

        self._email_queue.enqueue_send_activation(
            user_id=member.id,
            email=member.email,
            locale=member.preferred_locale.value,
            frontend_url=self._frontend_url,
            welcome=False,
        )
        return Ok(None)
