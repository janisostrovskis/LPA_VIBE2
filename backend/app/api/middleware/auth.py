"""FastAPI dependency for JWT-protected routes."""

from __future__ import annotations

from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies import get_auth_service
from app.application.ports.auth_service import AuthService
from app.lib.result import Ok

_bearer = HTTPBearer()


async def require_auth(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> dict[str, object]:
    """Validate the Bearer token and return the decoded JWT payload.

    Raises HTTP 401 if the token is missing, expired, or invalid.
    """
    result = auth_service.validate_token(credentials.credentials)
    if not isinstance(result, Ok):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result.value


async def require_member_id(
    payload: Annotated[dict[str, object], Depends(require_auth)],
) -> UUID:
    """Extract and return the member UUID from the JWT subject claim."""
    return UUID(str(payload["sub"]))
