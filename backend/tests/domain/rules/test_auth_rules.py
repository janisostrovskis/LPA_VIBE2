"""Tests for auth_rules pure functions."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from app.domain.rules.auth_rules import (
    is_magic_link_expired,
    is_magic_link_used,
    validate_password_strength,
)


class TestValidatePasswordStrength:
    def test_valid_password(self) -> None:
        assert validate_password_strength("SecureP4ss") == []

    def test_too_short(self) -> None:
        failures = validate_password_strength("Sh0rt")
        assert any("8 characters" in f for f in failures)

    def test_missing_uppercase(self) -> None:
        failures = validate_password_strength("lowercase1")
        assert any("uppercase" in f for f in failures)

    def test_missing_lowercase(self) -> None:
        failures = validate_password_strength("UPPERCASE1")
        assert any("lowercase" in f for f in failures)

    def test_missing_digit(self) -> None:
        failures = validate_password_strength("NoDigitHere")
        assert any("digit" in f for f in failures)

    def test_multiple_failures(self) -> None:
        # Only uppercase letters — no lowercase, no digit
        failures = validate_password_strength("ABCDEFGH")
        assert len(failures) >= 2

    def test_empty_string(self) -> None:
        failures = validate_password_strength("")
        # Fails all four rules
        assert len(failures) == 4

    def test_exactly_eight_valid_chars(self) -> None:
        assert validate_password_strength("Validp4s") == []


class TestIsMagicLinkExpired:
    def _utc(self, **kwargs: int) -> datetime:
        return datetime.now(tz=UTC) + timedelta(**kwargs)

    def test_expired(self) -> None:
        expires_at = self._utc(seconds=-1)
        assert is_magic_link_expired(expires_at) is True

    def test_not_expired(self) -> None:
        expires_at = self._utc(hours=1)
        assert is_magic_link_expired(expires_at) is False

    def test_exact_boundary_is_expired(self) -> None:
        # When now == expires_at the link is considered expired.
        fixed = datetime(2030, 1, 1, 12, 0, 0, tzinfo=UTC)
        assert is_magic_link_expired(expires_at=fixed, now=fixed) is True

    def test_naive_expires_at_treated_as_utc(self) -> None:
        naive_past = datetime(2000, 1, 1)  # far in the past, no tzinfo
        assert is_magic_link_expired(naive_past) is True

    def test_naive_now_treated_as_utc(self) -> None:
        naive_future = datetime(2099, 1, 1)
        naive_now = datetime(2000, 1, 1)
        assert is_magic_link_expired(expires_at=naive_future, now=naive_now) is False


class TestIsMagicLinkUsed:
    def test_used(self) -> None:
        assert is_magic_link_used(True) is True

    def test_not_used(self) -> None:
        assert is_magic_link_used(False) is False
