"""Tests for RegisterMember use case."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from app.application.dto.member_dto import MemberCreateDto, MemberDto
from app.application.use_cases.auth.register import RegisterMember
from app.domain.entities.member import Member
from app.domain.errors.auth_error import EmailAlreadyRegisteredError, WeakPasswordError
from app.domain.value_objects.locale import Locale
from app.lib.errors import ValidationError
from app.lib.result import Err, Ok
from tests.application._doubles.email_queue import FakeEmailQueue


def _make_member(email: str = "test@example.com") -> Member:
    now = datetime.now(tz=UTC)
    return Member(
        id=uuid4(),
        email=email,
        display_name="Test User",
        preferred_locale=Locale.LV,
        password_hash="hashed",
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_register_success() -> None:
    member_repo = AsyncMock()
    member_repo.get_by_email.return_value = None
    member_repo.create.side_effect = lambda m: m
    fake_queue = FakeEmailQueue()

    use_case = RegisterMember(
        member_repo=member_repo,
        hash_fn=lambda p: "hashed_" + p,
        email_queue=fake_queue,
        frontend_url="http://localhost:3001",
    )
    dto = MemberCreateDto(
        email="new@example.com",
        display_name="Alice",
        password="Password1",  # pragma: allowlist secret
    )
    result = await use_case.execute(dto)

    assert isinstance(result, Ok)
    assert isinstance(result.value, MemberDto)
    assert result.value.email == "new@example.com"

    # Activation email must have been enqueued
    assert len(fake_queue.calls) == 1
    call = fake_queue.calls[0]
    assert call["email"] == "new@example.com"
    assert call["welcome"] is True
    assert call["locale"] == "lv"
    assert call["frontend_url"] == "http://localhost:3001"


@pytest.mark.asyncio
async def test_register_duplicate_email() -> None:
    member_repo = AsyncMock()
    member_repo.get_by_email.return_value = _make_member("existing@example.com")

    use_case = RegisterMember(
        member_repo=member_repo,
        hash_fn=lambda p: "hashed_" + p,
        email_queue=FakeEmailQueue(),
        frontend_url="http://localhost:3001",
    )
    dto = MemberCreateDto(
        email="existing@example.com",
        display_name="Bob",
        password="Password1",  # pragma: allowlist secret
    )
    result = await use_case.execute(dto)

    assert isinstance(result, Err)
    assert isinstance(result.error, EmailAlreadyRegisteredError)


@pytest.mark.asyncio
async def test_register_weak_password() -> None:
    member_repo = AsyncMock()
    member_repo.get_by_email.return_value = None

    use_case = RegisterMember(
        member_repo=member_repo,
        hash_fn=lambda p: "hashed_" + p,
        email_queue=FakeEmailQueue(),
        frontend_url="http://localhost:3001",
    )
    dto = MemberCreateDto(email="valid@example.com", display_name="Carol", password="weak")
    result = await use_case.execute(dto)

    assert isinstance(result, Err)
    assert isinstance(result.error, WeakPasswordError)


@pytest.mark.asyncio
async def test_register_invalid_email() -> None:
    member_repo = AsyncMock()

    use_case = RegisterMember(
        member_repo=member_repo,
        hash_fn=lambda p: "hashed_" + p,
        email_queue=FakeEmailQueue(),
        frontend_url="http://localhost:3001",
    )
    dto = MemberCreateDto(
        email="not-an-email",
        display_name="Dave",
        password="Password1",  # pragma: allowlist secret
    )
    result = await use_case.execute(dto)

    assert isinstance(result, Err)
    assert isinstance(result.error, ValidationError)
