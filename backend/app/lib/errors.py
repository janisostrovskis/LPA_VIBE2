"""Domain error taxonomy. Framework-free; safe to import from the Domain layer.

HTTP status mapping lives in the API adapter layer (Phase 1), not here.
"""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import ClassVar


@dataclass(frozen=True)
class DomainError:
    message: str
    details: Mapping[str, object] | None = None
    code: ClassVar[str] = "domain_error"


@dataclass(frozen=True)
class NotFoundError(DomainError):
    code: ClassVar[str] = "not_found"


@dataclass(frozen=True)
class ValidationError(DomainError):
    code: ClassVar[str] = "validation_error"


@dataclass(frozen=True)
class ConflictError(DomainError):
    code: ClassVar[str] = "conflict"


@dataclass(frozen=True)
class UnauthorizedError(DomainError):
    code: ClassVar[str] = "unauthorized"


@dataclass(frozen=True)
class ForbiddenError(DomainError):
    code: ClassVar[str] = "forbidden"
