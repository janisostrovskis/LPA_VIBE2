"""Tests for password_service utility functions."""

from __future__ import annotations

from app.infrastructure.auth.password_service import hash_password, verify_password


def test_hash_and_verify_round_trip() -> None:
    hashed = hash_password("correct-horse-battery-staple")
    assert verify_password("correct-horse-battery-staple", hashed) is True


def test_wrong_password_returns_false() -> None:
    hashed = hash_password("secret-password")
    assert verify_password("wrong-password", hashed) is False


def test_different_hashes_for_same_password() -> None:
    """bcrypt salts each hash — two calls must produce distinct digests."""
    pw = "same-password"
    hash_a = hash_password(pw)
    hash_b = hash_password(pw)
    assert hash_a != hash_b
    # Both must still verify correctly
    assert verify_password(pw, hash_a) is True
    assert verify_password(pw, hash_b) is True
