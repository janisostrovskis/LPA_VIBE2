"""FastAPI router for authentication endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies import (
    get_auth_service,
    get_email_sender,
    get_magic_link_repo,
    get_member_repo,
)
from app.api.routes._errors import result_to_response
from app.application.dto.auth_dto import (
    LoginRequest,
    MagicLinkRequest,
    MagicLinkVerifyRequest,
    TokenResponse,
)
from app.application.dto.member_dto import MemberCreateDto, MemberDto
from app.application.ports.auth_service import AuthService
from app.application.ports.email_sender import EmailSender
from app.application.ports.magic_link_repository import MagicLinkRepository
from app.application.ports.member_repository import MemberRepository
from app.application.use_cases.auth.login_magic_link import RequestMagicLink, VerifyMagicLink
from app.application.use_cases.auth.login_password import LoginWithPassword
from app.application.use_cases.auth.refresh_token import RefreshToken
from app.application.use_cases.auth.register import RegisterMember
from app.infrastructure.auth.password_service import hash_password, verify_password

_bearer = HTTPBearer()
router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=MemberDto)
async def register(
    body: MemberCreateDto,
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
) -> MemberDto:
    """Register a new LPA member with email and password."""
    use_case = RegisterMember(member_repo=member_repo, hash_fn=hash_password)
    result = await use_case.execute(body)
    return result_to_response(result, success_status=status.HTTP_201_CREATED)


@router.post("/login", response_model=TokenResponse)
async def login(
    body: LoginRequest,
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Authenticate with email and password, returning a JWT."""
    use_case = LoginWithPassword(
        member_repo=member_repo,
        auth_service=auth_service,
        verify_fn=verify_password,
    )
    result = await use_case.execute(body)
    return result_to_response(result)


@router.post("/magic-link/request", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def request_magic_link(
    body: MagicLinkRequest,
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
    magic_link_repo: Annotated[MagicLinkRepository, Depends(get_magic_link_repo)],
    email_sender: Annotated[EmailSender, Depends(get_email_sender)],
) -> None:
    """Send a magic-link login email to the given address."""
    use_case = RequestMagicLink(
        member_repo=member_repo,
        magic_link_repo=magic_link_repo,
        email_sender=email_sender,
    )
    result = await use_case.execute(body)
    result_to_response(result, success_status=status.HTTP_204_NO_CONTENT)


@router.post("/magic-link/verify", response_model=TokenResponse)
async def verify_magic_link(
    body: MagicLinkVerifyRequest,
    magic_link_repo: Annotated[MagicLinkRepository, Depends(get_magic_link_repo)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Consume a magic-link token and return a JWT on success."""
    use_case = VerifyMagicLink(magic_link_repo=magic_link_repo, auth_service=auth_service)
    result = await use_case.execute(body)
    return result_to_response(result)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Refresh an existing JWT, returning a new token with the same subject."""
    use_case = RefreshToken(auth_service=auth_service)
    result = await use_case.execute(credentials.credentials)
    return result_to_response(result)
