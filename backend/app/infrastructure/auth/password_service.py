"""Password hashing utilities using bcrypt directly."""

from __future__ import annotations

import bcrypt


def hash_password(password: str) -> str:
    """Return a bcrypt hash of the given plaintext password."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Return True if password matches the bcrypt hash, False otherwise."""
    return bcrypt.checkpw(password.encode(), hashed.encode())
