"""Tests for /api/auth routes."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import (
    get_auth_service,
    get_email_queue,
    get_email_sender,
    get_magic_link_repo,
    get_member_repo,
)
from app.application.ports.auth_service import AuthService
from app.application.ports.member_repository import MemberRepository
from app.domain.entities.member import Member
from app.domain.errors.auth_error import EmailAlreadyRegisteredError, InvalidCredentialsError
from app.domain.value_objects.locale import Locale
from app.lib.result import Err, Ok
from app.main import app
from tests.application._doubles.email_queue import FakeEmailQueue


def _make_member(email: str = "user@example.com") -> Member:
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


def _make_auth_service(token: str = "test-token") -> AuthService:
    svc = MagicMock(spec=AuthService)
    svc.issue_token.return_value = token
    svc.validate_token.return_value = Ok({"sub": str(uuid4())})
    return svc


@pytest.fixture(autouse=True)
def _clear_overrides() -> None:  # type: ignore[return]
    """Remove dependency overrides after each test to prevent leakage."""
    yield  # type: ignore[misc]
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health() -> None:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_register_success() -> None:
    member_repo = AsyncMock(spec=MemberRepository)
    member_repo.get_by_email.return_value = None
    member_repo.create.side_effect = lambda m: m
    fake_queue = FakeEmailQueue()

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_email_queue] = lambda: fake_queue

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "new@example.com",
                "display_name": "Alice",
                "password": "Password1",  # pragma: allowlist secret
            },
        )

    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "new@example.com"
    assert data["display_name"] == "Alice"
    # Activation email must have been enqueued
    assert len(fake_queue.calls) == 1
    assert fake_queue.calls[0]["email"] == "new@example.com"
    assert fake_queue.calls[0]["welcome"] is True


@pytest.mark.asyncio
async def test_register_duplicate_email() -> None:
    member_repo = AsyncMock(spec=MemberRepository)
    member_repo.get_by_email.return_value = _make_member("existing@example.com")

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_email_queue] = lambda: FakeEmailQueue()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "email": "existing@example.com",
                "display_name": "Bob",
                "password": "Password1",  # pragma: allowlist secret
            },
        )

    assert response.status_code == 409
    detail = response.json()["detail"]
    assert detail["code"] == "email_already_registered"
    assert "already" in detail["message"].lower()


@pytest.mark.asyncio
async def test_login_success() -> None:
    import bcrypt

    plain = "Password1"  # pragma: allowlist secret
    hashed = bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()
    member = _make_member("user@example.com")
    member.password_hash = hashed

    member_repo = AsyncMock(spec=MemberRepository)
    member_repo.get_by_email.return_value = member

    auth_service = _make_auth_service("jwt-token")

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_auth_service] = lambda: auth_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "Password1"},  # pragma: allowlist secret
        )

    assert response.status_code == 200
    data = response.json()
    assert data["access_token"] == "jwt-token"
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password() -> None:
    import bcrypt

    hashed = bcrypt.hashpw(b"correct-pw", bcrypt.gensalt()).decode()  # pragma: allowlist secret
    member = _make_member("user@example.com")
    member.password_hash = hashed

    member_repo = AsyncMock(spec=MemberRepository)
    member_repo.get_by_email.return_value = member

    auth_service = _make_auth_service()

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_auth_service] = lambda: auth_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={"email": "user@example.com", "password": "wrong-password"},  # pragma: allowlist secret
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email() -> None:
    member_repo = AsyncMock(spec=MemberRepository)
    member_repo.get_by_email.return_value = None

    auth_service = _make_auth_service()

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_auth_service] = lambda: auth_service

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            json={"email": "nobody@example.com", "password": "Password1"},  # pragma: allowlist secret
        )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_resend_activation_returns_204() -> None:
    member_repo = AsyncMock(spec=MemberRepository)
    member_repo.get_by_email.return_value = None  # email-enum safe: always 204

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_email_queue] = lambda: FakeEmailQueue()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/auth/resend-activation",
            json={"email": "nobody@example.com"},
        )

    assert response.status_code == 204
