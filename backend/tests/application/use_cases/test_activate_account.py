"""Tests for ActivateAccount and ResendActivation use cases."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest

from app.application.dto.auth_dto import TokenResponse
from app.application.use_cases.auth.activate_account import ActivateAccount, ResendActivation
from app.domain.entities.member import Member
from app.domain.errors.auth_error import ActivationTokenInvalidError
from app.domain.value_objects.locale import Locale
from app.lib.result import Err, Ok
from tests.application._doubles.email_queue import FakeEmailQueue


def _make_member(
    email: str = "user@example.com",
    is_active: bool = False,
) -> Member:
    now = datetime.now(tz=UTC)
    return Member(
        id=uuid4(),
        email=email,
        display_name="Test User",
        preferred_locale=Locale.LV,
        password_hash="hashed",
        is_active=is_active,
        created_at=now,
        updated_at=now,
    )


class TestActivateAccount:
    @pytest.mark.asyncio
    async def test_activate_success(self) -> None:
        member = _make_member(is_active=False)
        magic_link_repo = AsyncMock()
        magic_link_repo.consume.return_value = (
            member.id,
            datetime.now(tz=UTC) + timedelta(hours=24),
        )
        member_repo = AsyncMock()
        member_repo.get_by_id.return_value = member
        auth_service = MagicMock()
        auth_service.issue_token.return_value = "jwt-token"

        use_case = ActivateAccount(
            member_repo=member_repo,
            magic_link_repo=magic_link_repo,
            auth_service=auth_service,
        )
        result = await use_case.execute("valid-token")

        assert isinstance(result, Ok)
        assert isinstance(result.value, TokenResponse)
        assert result.value.access_token == "jwt-token"
        member_repo.update.assert_called_once()

    @pytest.mark.asyncio
    async def test_activate_invalid_token(self) -> None:
        magic_link_repo = AsyncMock()
        magic_link_repo.consume.return_value = None
        member_repo = AsyncMock()
        auth_service = MagicMock()

        use_case = ActivateAccount(
            member_repo=member_repo,
            magic_link_repo=magic_link_repo,
            auth_service=auth_service,
        )
        result = await use_case.execute("bad-token")

        assert isinstance(result, Err)
        assert isinstance(result.error, ActivationTokenInvalidError)

    @pytest.mark.asyncio
    async def test_activate_expired_token(self) -> None:
        member = _make_member(is_active=False)
        magic_link_repo = AsyncMock()
        magic_link_repo.consume.return_value = (
            member.id,
            datetime.now(tz=UTC) - timedelta(hours=1),
        )
        member_repo = AsyncMock()
        auth_service = MagicMock()

        use_case = ActivateAccount(
            member_repo=member_repo,
            magic_link_repo=magic_link_repo,
            auth_service=auth_service,
        )
        result = await use_case.execute("expired-token")

        assert isinstance(result, Err)
        assert isinstance(result.error, ActivationTokenInvalidError)


class TestResendActivation:
    @pytest.mark.asyncio
    async def test_resend_enqueues_for_inactive_member(self) -> None:
        member = _make_member(is_active=False)
        member_repo = AsyncMock()
        member_repo.get_by_email.return_value = member
        fake_queue = FakeEmailQueue()

        use_case = ResendActivation(
            member_repo=member_repo,
            email_queue=fake_queue,
            frontend_url="http://localhost:3001",
        )
        result = await use_case.execute("user@example.com")

        assert isinstance(result, Ok)
        assert len(fake_queue.calls) == 1
        call = fake_queue.calls[0]
        assert call["email"] == "user@example.com"
        assert call["welcome"] is False
        assert call["frontend_url"] == "http://localhost:3001"

    @pytest.mark.asyncio
    async def test_resend_noop_for_unknown_email(self) -> None:
        member_repo = AsyncMock()
        member_repo.get_by_email.return_value = None
        fake_queue = FakeEmailQueue()

        use_case = ResendActivation(
            member_repo=member_repo,
            email_queue=fake_queue,
            frontend_url="http://localhost:3001",
        )
        result = await use_case.execute("nobody@example.com")

        assert isinstance(result, Ok)
        assert len(fake_queue.calls) == 0

    @pytest.mark.asyncio
    async def test_resend_noop_for_already_active_member(self) -> None:
        member = _make_member(is_active=True)
        member_repo = AsyncMock()
        member_repo.get_by_email.return_value = member
        fake_queue = FakeEmailQueue()

        use_case = ResendActivation(
            member_repo=member_repo,
            email_queue=fake_queue,
            frontend_url="http://localhost:3001",
        )
        result = await use_case.execute("user@example.com")

        assert isinstance(result, Ok)
        assert len(fake_queue.calls) == 0
