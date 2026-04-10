"""Authentication business invariant rules.

Pure functions — no side effects, no framework imports.
"""

from __future__ import annotations

from datetime import UTC, datetime


def validate_password_strength(password: str) -> list[str]:
    """Return a list of failure reasons; empty list means the password is valid.

    Rules: minimum 8 characters, at least one uppercase letter,
    one lowercase letter, and one digit.
    """
    failures: list[str] = []
    if len(password) < 8:
        failures.append("Password must be at least 8 characters long.")
    if not any(c.isupper() for c in password):
        failures.append("Password must contain at least one uppercase letter.")
    if not any(c.islower() for c in password):
        failures.append("Password must contain at least one lowercase letter.")
    if not any(c.isdigit() for c in password):
        failures.append("Password must contain at least one digit.")
    return failures


def is_magic_link_expired(expires_at: datetime, now: datetime | None = None) -> bool:
    """Return True if the magic link has expired.

    *now* defaults to UTC now and exists to allow deterministic testing.
    """
    effective_now = now if now is not None else datetime.now(tz=UTC)
    # Normalise naive datetimes (assume UTC) so comparison is always tz-aware.
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if effective_now.tzinfo is None:
        effective_now = effective_now.replace(tzinfo=UTC)
    return effective_now >= expires_at


def is_magic_link_used(used: bool) -> bool:
    """Return True if the magic link has already been consumed."""
    return used
