"""Tests for JWTService."""

from __future__ import annotations

import time

from app.infrastructure.auth.jwt_service import JWTService
from app.lib.errors import UnauthorizedError
from app.lib.result import Err, Ok

_SECRET = "test-secret-key-that-is-long-enough"


def test_issue_and_validate_round_trip() -> None:
    svc = JWTService(secret=_SECRET)
    token = svc.issue_token(subject="user-123")
    result = svc.validate_token(token)
    assert isinstance(result, Ok)
    assert result.value["sub"] == "user-123"


def test_custom_claims_preserved() -> None:
    svc = JWTService(secret=_SECRET)
    token = svc.issue_token(subject="user-456", claims={"role": "admin", "org": "lpa"})
    result = svc.validate_token(token)
    assert isinstance(result, Ok)
    assert result.value["sub"] == "user-456"
    assert result.value["role"] == "admin"
    assert result.value["org"] == "lpa"


def test_expired_token_returns_err() -> None:
    svc = JWTService(secret=_SECRET, expiry_minutes=0)
    token = svc.issue_token(subject="user-789")
    # Wait just long enough for the 0-minute token to expire (1 second covers it)
    time.sleep(1)
    result = svc.validate_token(token)
    assert isinstance(result, Err)
    assert isinstance(result.error, UnauthorizedError)
    assert "expired" in result.error.message.lower()


def test_tampered_token_returns_err() -> None:
    svc = JWTService(secret=_SECRET)
    token = svc.issue_token(subject="user-000")
    tampered = token[:-4] + "xxxx"
    result = svc.validate_token(tampered)
    assert isinstance(result, Err)
    assert isinstance(result.error, UnauthorizedError)


def test_invalid_token_string_returns_err() -> None:
    svc = JWTService(secret=_SECRET)
    result = svc.validate_token("not.a.valid.jwt")
    assert isinstance(result, Err)
    assert isinstance(result.error, UnauthorizedError)


def test_wrong_secret_returns_err() -> None:
    svc_a = JWTService(secret=_SECRET)
    svc_b = JWTService(secret="different-secret-key-also-long")
    token = svc_a.issue_token(subject="user-111")
    result = svc_b.validate_token(token)
    assert isinstance(result, Err)
    assert isinstance(result.error, UnauthorizedError)
