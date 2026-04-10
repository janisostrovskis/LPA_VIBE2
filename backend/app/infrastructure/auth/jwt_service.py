"""JWT implementation of AuthService using PyJWT with HS256."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import jwt

from app.application.ports.auth_service import AuthService
from app.lib.errors import UnauthorizedError
from app.lib.logger import get_logger
from app.lib.result import Err, Ok, Result

_logger = get_logger(__name__)


class JWTService(AuthService):
    """Issues and validates HS256 JWTs."""

    def __init__(self, secret: str, expiry_minutes: int = 60) -> None:
        if not secret:
            raise ValueError("JWT secret must not be empty")
        self._secret = secret
        self._expiry_minutes = expiry_minutes

    def issue_token(self, subject: str, claims: dict[str, object] | None = None) -> str:
        now = datetime.now(tz=UTC)
        payload: dict[str, object] = {
            "sub": subject,
            "iat": now,
            "exp": now + timedelta(minutes=self._expiry_minutes),
        }
        if claims:
            payload.update(claims)
        return jwt.encode(payload, self._secret, algorithm="HS256")

    def validate_token(self, token: str) -> Result[dict[str, object], UnauthorizedError]:
        try:
            payload: dict[str, object] = jwt.decode(
                token,
                self._secret,
                algorithms=["HS256"],
            )
        except jwt.ExpiredSignatureError:
            _logger.warning("JWT validation failed: token expired")
            return Err(UnauthorizedError(message="Token has expired"))
        except jwt.InvalidTokenError as exc:
            _logger.warning("JWT validation failed: %s", exc)
            return Err(UnauthorizedError(message="Invalid token"))
        return Ok(payload)
