"""Tests for the Email value object."""

import pytest

from app.domain.value_objects.email import Email


class TestEmailCreate:
    def test_valid_basic(self) -> None:
        email = Email.create("user@example.com")
        assert email.value == "user@example.com"

    def test_valid_subdomain(self) -> None:
        email = Email.create("user@mail.example.co.uk")
        assert email.value == "user@mail.example.co.uk"

    def test_valid_plus_addressing(self) -> None:
        email = Email.create("user+tag@example.com")
        assert email.value == "user+tag@example.com"

    def test_normalization_to_lowercase(self) -> None:
        email = Email.create("User@Example.COM")
        assert email.value == "user@example.com"

    def test_strips_surrounding_whitespace(self) -> None:
        email = Email.create("  user@example.com  ")
        assert email.value == "user@example.com"

    def test_invalid_no_at_sign(self) -> None:
        with pytest.raises(ValueError):
            Email.create("userexample.com")

    def test_invalid_no_domain(self) -> None:
        with pytest.raises(ValueError):
            Email.create("user@")

    def test_invalid_empty_string(self) -> None:
        with pytest.raises(ValueError):
            Email.create("")

    def test_invalid_whitespace_only(self) -> None:
        with pytest.raises(ValueError):
            Email.create("   ")

    def test_invalid_missing_tld(self) -> None:
        with pytest.raises(ValueError):
            Email.create("user@example")


class TestEmailImmutability:
    def test_frozen_dataclass(self) -> None:
        email = Email.create("user@example.com")
        with pytest.raises((AttributeError, TypeError)):
            email.value = "other@example.com"  # type: ignore[misc]

    def test_equality_by_value(self) -> None:
        a = Email.create("user@example.com")
        b = Email.create("USER@EXAMPLE.COM")
        assert a == b

    def test_str_returns_value(self) -> None:
        email = Email.create("user@example.com")
        assert str(email) == "user@example.com"
