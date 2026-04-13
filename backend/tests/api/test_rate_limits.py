"""Tests for per-IP rate limits on auth endpoints.

IMPORTANT: os.environ must be set BEFORE any app imports because
`app.api.middleware.rate_limit` captures `get_settings()` at module import
time (lru_cache singleton). Setting memory:// here ensures the Limiter uses
an in-process store rather than the Redis URL that may not be available in CI.
"""

from __future__ import annotations

import os

# Must precede all app imports — rate_limit.py reads settings at import time.
os.environ["RATE_LIMIT_REDIS_URL"] = "memory://"
os.environ["RATE_LIMIT_ENABLED"] = "true"
os.environ["DATABASE_URL"] = os.environ.get("DATABASE_URL", "postgresql+asyncpg://lpa:lpa@db:5432/lpa")

from unittest.mock import AsyncMock, MagicMock  # noqa: E402
from uuid import uuid4  # noqa: E402

import pytest  # noqa: E402
from httpx import ASGITransport, AsyncClient  # noqa: E402

from app.api.dependencies import (  # noqa: E402
    get_auth_service,
    get_email_queue,
    get_email_sender,
    get_magic_link_repo,
    get_member_repo,
)
from app.api.middleware.rate_limit import limiter  # noqa: E402
from app.application.ports.auth_service import AuthService  # noqa: E402
from app.application.ports.member_repository import MemberRepository  # noqa: E402
from app.lib.result import Err  # noqa: E402
from app.main import app  # noqa: E402
from tests.application._doubles.email_queue import FakeEmailQueue  # noqa: E402


# ---------------------------------------------------------------------------
# Shared doubles
# ---------------------------------------------------------------------------

def _make_auth_service() -> AuthService:
    svc = MagicMock(spec=AuthService)
    svc.issue_token.return_value = "tok"
    svc.validate_token.return_value = Err(MagicMock())
    return svc


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _reset_limiter_and_overrides() -> None:  # type: ignore[return]
    """Reset in-memory rate-limit counters and dependency overrides between tests."""
    limiter.reset()
    yield  # type: ignore[misc]
    app.dependency_overrides.clear()
    limiter.reset()


# ---------------------------------------------------------------------------
# Login — 5/minute
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_login_rate_limit_triggers_429() -> None:
    member_repo = AsyncMock(spec=MemberRepository)
    member_repo.get_by_email.return_value = None  # always 401 (unknown email)

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_auth_service] = lambda: _make_auth_service()

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Forwarded-For": f"10.0.{uuid4().int % 256}.1"},
    ) as client:
        for i in range(5):
            r = await client.post(
                "/api/auth/login",
                json={"email": "x@example.com", "password": "wrong"},  # pragma: allowlist secret
            )
            assert r.status_code == 401, f"request {i + 1} expected 401, got {r.status_code}"

        r = await client.post(
            "/api/auth/login",
            json={"email": "x@example.com", "password": "wrong"},  # pragma: allowlist secret
        )
    assert r.status_code == 429
    assert r.json()["detail"]["code"] == "rate_limited"
    assert "Retry-After" in r.headers


# ---------------------------------------------------------------------------
# Register — 3/hour
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_register_rate_limit_triggers_429() -> None:
    member_repo = AsyncMock(spec=MemberRepository)
    member_repo.get_by_email.return_value = None
    member_repo.create.side_effect = lambda m: m
    fake_queue = FakeEmailQueue()

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_email_queue] = lambda: fake_queue

    ip = f"10.1.{uuid4().int % 256}.1"

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Forwarded-For": ip},
    ) as client:
        for i in range(3):
            r = await client.post(
                "/api/auth/register",
                json={
                    "email": f"u{i}@example.com",
                    "display_name": f"User{i}",
                    "password": "Password1",  # pragma: allowlist secret
                },
            )
            assert r.status_code == 201, f"request {i + 1} expected 201, got {r.status_code}"

        r = await client.post(
            "/api/auth/register",
            json={
                "email": "extra@example.com",
                "display_name": "Extra",
                "password": "Password1",  # pragma: allowlist secret
            },
        )
    assert r.status_code == 429


# ---------------------------------------------------------------------------
# Resend-activation — 3/minute
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_resend_activation_rate_limit_triggers_429() -> None:
    member_repo = AsyncMock(spec=MemberRepository)
    member_repo.get_by_email.return_value = None

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_email_queue] = lambda: FakeEmailQueue()

    ip = f"10.2.{uuid4().int % 256}.1"

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Forwarded-For": ip},
    ) as client:
        for i in range(3):
            r = await client.post(
                "/api/auth/resend-activation",
                json={"email": "nobody@example.com"},
            )
            assert r.status_code == 204, f"request {i + 1} expected 204, got {r.status_code}"

        r = await client.post(
            "/api/auth/resend-activation",
            json={"email": "nobody@example.com"},
        )
    assert r.status_code == 429


# ---------------------------------------------------------------------------
# Magic-link/request — 5/minute (stacked with 20/hour)
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_magic_link_request_rate_limit_triggers_429() -> None:
    member_repo = AsyncMock(spec=MemberRepository)
    member_repo.get_by_email.return_value = None
    magic_link_repo = AsyncMock()
    email_sender = AsyncMock()

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_magic_link_repo] = lambda: magic_link_repo
    app.dependency_overrides[get_email_sender] = lambda: email_sender

    ip = f"10.3.{uuid4().int % 256}.1"

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Forwarded-For": ip},
    ) as client:
        for i in range(5):
            r = await client.post(
                "/api/auth/magic-link/request",
                json={"email": "x@example.com"},
            )
            assert r.status_code in (204, 200), (
                f"request {i + 1} unexpected status {r.status_code}"
            )

        r = await client.post(
            "/api/auth/magic-link/request",
            json={"email": "x@example.com"},
        )
    assert r.status_code == 429


# ---------------------------------------------------------------------------
# Activate — 10/minute
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_activate_rate_limit_triggers_429() -> None:
    member_repo = AsyncMock(spec=MemberRepository)
    magic_link_repo = AsyncMock()
    auth_service = _make_auth_service()
    # Simulate token-not-found / invalid to get a non-200 but not 429
    magic_link_repo.consume.return_value = None

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_magic_link_repo] = lambda: magic_link_repo
    app.dependency_overrides[get_auth_service] = lambda: auth_service

    ip = f"10.4.{uuid4().int % 256}.1"

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Forwarded-For": ip},
    ) as client:
        for i in range(10):
            r = await client.post(
                "/api/auth/activate",
                json={"token": "bad-token"},
            )
            assert r.status_code != 429, f"request {i + 1} hit 429 too early"

        r = await client.post(
            "/api/auth/activate",
            json={"token": "bad-token"},
        )
    assert r.status_code == 429


# ---------------------------------------------------------------------------
# Error envelope shape
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_rate_limit_error_envelope_shape() -> None:
    """The 429 response must use the project error envelope."""
    member_repo = AsyncMock(spec=MemberRepository)
    member_repo.get_by_email.return_value = None

    app.dependency_overrides[get_member_repo] = lambda: member_repo
    app.dependency_overrides[get_auth_service] = lambda: _make_auth_service()

    ip = f"10.5.{uuid4().int % 256}.1"

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"X-Forwarded-For": ip},
    ) as client:
        for _ in range(5):
            await client.post(
                "/api/auth/login",
                json={"email": "x@example.com", "password": "pw"},  # pragma: allowlist secret
            )
        r = await client.post(
            "/api/auth/login",
            json={"email": "x@example.com", "password": "pw"},  # pragma: allowlist secret
        )

    assert r.status_code == 429
    body = r.json()
    assert body == {
        "detail": {
            "code": "rate_limited",
            "message": "Too many requests. Try again later.",
        }
    }
    assert "Retry-After" in r.headers
