"""Tests for LoginWithPassword use case."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dto.auth_dto import LoginRequest, TokenResponse
from app.application.use_cases.auth.login_password import LoginWithPassword
from app.domain.entities.member import Member
from app.domain.errors.auth_error import InvalidCredentialsError
from app.domain.value_objects.locale import Locale
from app.lib.result import Err, Ok


def _make_member(password_hash: str | None = "hashed_Password1") -> Member:
    now = datetime.now(tz=UTC)
    return Member(
        id=uuid4(),
        email="user@example.com",
        display_name="Test User",
        preferred_locale=Locale.LV,
        password_hash=password_hash,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def _make_use_case(
    member: Member | None,
    verify_result: bool = True,
) -> LoginWithPassword:
    member_repo = AsyncMock()
    member_repo.get_by_email.return_value = member

    auth_service = MagicMock()
    auth_service.issue_token.return_value = "jwt_token"

    return LoginWithPassword(
        member_repo=member_repo,
        auth_service=auth_service,
        verify_fn=lambda _p, _h: verify_result,
    )


@pytest.mark.asyncio
async def test_login_success() -> None:
    use_case = _make_use_case(member=_make_member(), verify_result=True)
    result = await use_case.execute(LoginRequest(email="user@example.com", password="Password1",  # pragma: allowlist secret
    ))

    assert isinstance(result, Ok)
    assert isinstance(result.value, TokenResponse)
    assert result.value.access_token == "jwt_token"


@pytest.mark.asyncio
async def test_login_wrong_password() -> None:
    use_case = _make_use_case(member=_make_member(), verify_result=False)
    result = await use_case.execute(LoginRequest(email="user@example.com", password="WrongPass1",  # pragma: allowlist secret
    ))

    assert isinstance(result, Err)
    assert isinstance(result.error, InvalidCredentialsError)


@pytest.mark.asyncio
async def test_login_unknown_email() -> None:
    use_case = _make_use_case(member=None)
    result = await use_case.execute(LoginRequest(email="unknown@example.com", password="Password1",  # pragma: allowlist secret
    ))

    assert isinstance(result, Err)
    assert isinstance(result.error, InvalidCredentialsError)


@pytest.mark.asyncio
async def test_login_magic_link_only_user() -> None:
    """Members with no password_hash (magic-link-only) cannot log in with password."""
    use_case = _make_use_case(member=_make_member(password_hash=None), verify_result=True)
    result = await use_case.execute(LoginRequest(email="user@example.com", password="Password1",  # pragma: allowlist secret
    ))

    assert isinstance(result, Err)
    assert isinstance(result.error, InvalidCredentialsError)
