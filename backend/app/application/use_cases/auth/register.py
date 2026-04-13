"""Use case: register a new LPA member."""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from uuid import uuid4

from app.application.dto.member_dto import MemberCreateDto, MemberDto
from app.application.ports.email_queue import EmailQueue
from app.application.ports.member_repository import MemberRepository
from app.domain.entities.member import Member
from app.domain.errors.auth_error import EmailAlreadyRegisteredError, WeakPasswordError
from app.domain.rules.auth_rules import validate_password_strength
from app.domain.value_objects.email import Email
from app.domain.value_objects.locale import Locale
from app.lib.errors import DomainError, ValidationError
from app.lib.result import Err, Ok, Result


class RegisterMember:
    """Register a new member with email + password.

    The member is created with ``is_active=False``.  An activation email is
    enqueued immediately so the member can confirm their address before
    logging in. The email is sent asynchronously by the Celery worker so
    this use case returns quickly regardless of email delivery latency.
    """

    def __init__(
        self,
        member_repo: MemberRepository,
        hash_fn: Callable[[str], str],
        email_queue: EmailQueue,
        frontend_url: str,
    ) -> None:
        self._member_repo = member_repo
        self._hash_fn = hash_fn
        self._email_queue = email_queue
        self._frontend_url = frontend_url

    async def execute(self, dto: MemberCreateDto) -> Result[MemberDto, DomainError]:
        try:
            email_vo = Email.create(dto.email)
        except ValueError as exc:
            return Err(ValidationError(message=str(exc)))

        failures = validate_password_strength(dto.password)
        if failures:
            return Err(WeakPasswordError(message="; ".join(failures)))

        existing = await self._member_repo.get_by_email(email_vo.value)
        if existing is not None:
            return Err(EmailAlreadyRegisteredError(message="Email already registered."))

        try:
            locale = Locale(dto.preferred_locale)
        except ValueError:
            return Err(ValidationError(message=f"Unsupported locale: {dto.preferred_locale!r}"))

        now = datetime.now(tz=UTC)
        member = Member(
            id=uuid4(),
            email=email_vo.value,
            display_name=dto.display_name,
            preferred_locale=locale,
            password_hash=self._hash_fn(dto.password),
            is_active=False,
            created_at=now,
            updated_at=now,
        )
        created = await self._member_repo.create(member)

        self._email_queue.enqueue_send_activation(
            user_id=created.id,
            email=created.email,
            locale=locale.value,
            frontend_url=self._frontend_url,
            welcome=True,
        )

        return Ok(MemberDto.from_entity(created))
