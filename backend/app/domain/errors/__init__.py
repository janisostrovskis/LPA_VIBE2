"""COLA domain layer — errors (typed domain error classes)."""

from app.domain.errors.auth_error import (
    EmailAlreadyRegisteredError,
    InsufficientRoleError,
    InvalidCredentialsError,
    MagicLinkExpiredError,
    WeakPasswordError,
)

__all__ = [
    "EmailAlreadyRegisteredError",
    "InsufficientRoleError",
    "InvalidCredentialsError",
    "MagicLinkExpiredError",
    "WeakPasswordError",
]
