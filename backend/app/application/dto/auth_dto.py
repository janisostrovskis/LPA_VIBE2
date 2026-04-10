"""DTOs for authentication requests and responses."""

from __future__ import annotations

from pydantic import BaseModel


class LoginRequest(BaseModel):
    """Password-based login credentials."""

    email: str
    password: str


class TokenResponse(BaseModel):
    """JWT bearer token returned on successful authentication."""

    access_token: str
    token_type: str = "bearer"  # noqa: S105


class MagicLinkRequest(BaseModel):
    """Request to send a magic-link email."""

    email: str


class MagicLinkVerifyRequest(BaseModel):
    """One-time token from a magic-link email."""

    token: str
