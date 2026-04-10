"""Port: abstract authentication service for JWT operations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.lib.errors import UnauthorizedError
from app.lib.result import Result


class AuthService(ABC):
    """Abstract service for issuing and validating JWT tokens."""

    @abstractmethod
    def issue_token(self, subject: str, claims: dict[str, object] | None = None) -> str:
        """Issue a JWT for the given subject (user ID)."""
        ...

    @abstractmethod
    def validate_token(self, token: str) -> Result[dict[str, object], UnauthorizedError]:
        """Validate and decode a JWT. Return Err(UnauthorizedError) if invalid/expired."""
        ...
