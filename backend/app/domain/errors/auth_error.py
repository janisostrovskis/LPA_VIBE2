"""Typed authentication domain errors.

All errors are frozen dataclasses inheriting from the correct base in
``app.lib.errors``.  HTTP status mapping lives in the API adapter layer.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from app.lib.errors import (
    ConflictError,
    ForbiddenError,
    UnauthorizedError,
    ValidationError,
)


@dataclass(frozen=True)
class InvalidCredentialsError(UnauthorizedError):
    code: ClassVar[str] = "invalid_credentials"


@dataclass(frozen=True)
class EmailAlreadyRegisteredError(ConflictError):
    code: ClassVar[str] = "email_already_registered"


@dataclass(frozen=True)
class MagicLinkExpiredError(ValidationError):
    code: ClassVar[str] = "magic_link_expired"


@dataclass(frozen=True)
class InsufficientRoleError(ForbiddenError):
    code: ClassVar[str] = "insufficient_role"


@dataclass(frozen=True)
class WeakPasswordError(ValidationError):
    code: ClassVar[str] = "weak_password"


@dataclass(frozen=True)
class AccountNotActivatedError(UnauthorizedError):
    code: ClassVar[str] = "account_not_activated"


@dataclass(frozen=True)
class ActivationTokenInvalidError(ValidationError):
    code: ClassVar[str] = "activation_token_invalid"
