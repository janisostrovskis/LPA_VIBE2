"""Use case: authenticate a member with email + password."""

from __future__ import annotations

from collections.abc import Callable

from app.application.dto.auth_dto import LoginRequest, TokenResponse
from app.application.ports.auth_service import AuthService
from app.application.ports.member_repository import MemberRepository
from app.domain.errors.auth_error import InvalidCredentialsError
from app.lib.errors import DomainError
from app.lib.result import Err, Ok, Result


class LoginWithPassword:
    """Authenticate a member using email and password, returning a JWT."""

    def __init__(
        self,
        member_repo: MemberRepository,
        auth_service: AuthService,
        verify_fn: Callable[[str, str], bool],
    ) -> None:
        self._member_repo = member_repo
        self._auth_service = auth_service
        self._verify_fn = verify_fn

    async def execute(self, dto: LoginRequest) -> Result[TokenResponse, DomainError]:
        member = await self._member_repo.get_by_email(dto.email.strip().lower())
        if member is None:
            return Err(InvalidCredentialsError(message="Invalid credentials."))

        if member.password_hash is None:
            return Err(InvalidCredentialsError(message="Invalid credentials."))

        if not self._verify_fn(dto.password, member.password_hash):
            return Err(InvalidCredentialsError(message="Invalid credentials."))

        token = self._auth_service.issue_token(str(member.id))
        return Ok(TokenResponse(access_token=token))
