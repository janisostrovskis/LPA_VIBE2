"""Use case: refresh a JWT by validating the current one and issuing a new one."""

from __future__ import annotations

from app.application.dto.auth_dto import TokenResponse
from app.application.ports.auth_service import AuthService
from app.lib.errors import DomainError
from app.lib.result import Err, Ok, Result


class RefreshToken:
    """Validate an existing JWT and issue a replacement with the same subject."""

    def __init__(self, auth_service: AuthService) -> None:
        self._auth_service = auth_service

    async def execute(self, token: str) -> Result[TokenResponse, DomainError]:
        claims_result = self._auth_service.validate_token(token)
        match claims_result:
            case Err(error=err):
                return Err(err)
            case Ok(value=claims):
                new_token = self._auth_service.issue_token(str(claims["sub"]))
                return Ok(TokenResponse(access_token=new_token))
