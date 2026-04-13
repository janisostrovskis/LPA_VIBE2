"""FastAPI router for authentication endpoints."""

# NOTE: do NOT re-add `from __future__ import annotations` here.
# slowapi's @limiter.limit() decorator uses functools.wraps, which copies the
# wrapped function's __annotations__ as strings. FastAPI resolves those strings
# from the *wrapper* function's __globals__ (the slowapi module), which does not
# contain the route's local types. Without PEP-563 postponed annotations, FastAPI
# receives actual type objects and resolves parameters correctly.
import os
from typing import Annotated

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.api.dependencies import (
    get_auth_service,
    get_email_queue,
    get_email_sender,
    get_magic_link_repo,
    get_member_repo,
)
from app.api.middleware.rate_limit import limiter
from app.api.routes._errors import result_to_response
from app.application.dto.auth_dto import (
    ActivateAccountRequest,
    LoginRequest,
    MagicLinkRequest,
    MagicLinkVerifyRequest,
    ResendActivationRequest,
    TokenResponse,
)
from app.application.dto.member_dto import MemberCreateDto, MemberDto
from app.application.ports.auth_service import AuthService
from app.application.ports.email_queue import EmailQueue
from app.application.ports.email_sender import EmailSender
from app.application.ports.magic_link_repository import MagicLinkRepository
from app.application.ports.member_repository import MemberRepository
from app.application.use_cases.auth.activate_account import ActivateAccount, ResendActivation
from app.application.use_cases.auth.login_magic_link import RequestMagicLink, VerifyMagicLink
from app.application.use_cases.auth.login_password import LoginWithPassword
from app.application.use_cases.auth.refresh_token import RefreshToken
from app.application.use_cases.auth.register import RegisterMember
from app.infrastructure.auth.password_service import hash_password, verify_password

_bearer = HTTPBearer()
router = APIRouter(prefix="/api/auth", tags=["auth"])

_DEFAULT_FRONTEND_URL = "http://localhost:3001"


def _get_frontend_url() -> str:
    return os.environ.get("FRONTEND_URL", _DEFAULT_FRONTEND_URL)


@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=MemberDto)
@limiter.limit("3/hour")
async def register(
    request: Request,
    body: MemberCreateDto,
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
    email_queue: Annotated[EmailQueue, Depends(get_email_queue)],
) -> MemberDto:
    """Register a new LPA member with email and password."""
    use_case = RegisterMember(
        member_repo=member_repo,
        hash_fn=hash_password,
        email_queue=email_queue,
        frontend_url=_get_frontend_url(),
    )
    result = await use_case.execute(body)
    return result_to_response(result, success_status=status.HTTP_201_CREATED)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
async def login(
    request: Request,
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
@limiter.limit("5/minute")
@limiter.limit("20/hour")
async def request_magic_link(
    request: Request,
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
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
) -> TokenResponse:
    """Consume a magic-link token and return a JWT on success."""
    use_case = VerifyMagicLink(
        magic_link_repo=magic_link_repo,
        auth_service=auth_service,
        member_repo=member_repo,
    )
    result = await use_case.execute(body)
    return result_to_response(result)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
) -> TokenResponse:
    """Refresh an existing JWT, returning a new token with the same subject."""
    use_case = RefreshToken(auth_service=auth_service, member_repo=member_repo)
    result = await use_case.execute(credentials.credentials)
    return result_to_response(result)


@router.post("/activate", response_model=TokenResponse)
@limiter.limit("10/minute")
async def activate_account(
    request: Request,
    body: ActivateAccountRequest,
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
    magic_link_repo: Annotated[MagicLinkRepository, Depends(get_magic_link_repo)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """Consume an activation token and return a JWT on success."""
    use_case = ActivateAccount(
        member_repo=member_repo,
        magic_link_repo=magic_link_repo,
        auth_service=auth_service,
    )
    result = await use_case.execute(body.token)
    return result_to_response(result)


@router.post("/resend-activation", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
@limiter.limit("3/minute")
@limiter.limit("10/hour")
async def resend_activation(
    request: Request,
    body: ResendActivationRequest,
    member_repo: Annotated[MemberRepository, Depends(get_member_repo)],
    email_queue: Annotated[EmailQueue, Depends(get_email_queue)],
) -> None:
    """Resend an activation email. Always returns 204 to prevent email enumeration."""
    use_case = ResendActivation(
        member_repo=member_repo,
        email_queue=email_queue,
        frontend_url=_get_frontend_url(),
    )
    result = await use_case.execute(body.email)
    result_to_response(result, success_status=status.HTTP_204_NO_CONTENT)
