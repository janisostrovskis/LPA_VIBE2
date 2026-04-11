"""Dependency injection wiring for the FastAPI API layer.

This is the ONLY file in the API layer that imports from infrastructure.
All other modules depend on ports (ABCs), wired here at runtime.
"""

from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.auth_service import AuthService
from app.application.ports.email_sender import EmailSender
from app.application.ports.magic_link_repository import MagicLinkRepository
from app.application.ports.member_repository import MemberRepository
from app.application.ports.organization_repository import OrganizationRepository
from app.infrastructure.auth.jwt_service import JWTService
from app.infrastructure.database.repositories.magic_link_repository import SqlaMagicLinkRepository
from app.infrastructure.database.repositories.member_repository import SqlaMemberRepository
from app.infrastructure.database.repositories.organization_repository import (
    SqlaOrganizationRepository,
)
from app.infrastructure.database.session import get_session
from app.infrastructure.config.env import get_settings

_JWT_EXPIRY_MINUTES = 60
_DEFAULT_JWT_SECRET = "dev-secret-change-me"  # noqa: S105  # pragma: allowlist secret


async def get_member_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncGenerator[MemberRepository, None]:
    """Wire SqlaMemberRepository to the MemberRepository port."""
    yield SqlaMemberRepository(session)


async def get_org_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncGenerator[OrganizationRepository, None]:
    """Wire SqlaOrganizationRepository to the OrganizationRepository port."""
    yield SqlaOrganizationRepository(session)


async def get_magic_link_repo(
    session: Annotated[AsyncSession, Depends(get_session)],
) -> AsyncGenerator[MagicLinkRepository, None]:
    """Wire SqlaMagicLinkRepository to the MagicLinkRepository port."""
    yield SqlaMagicLinkRepository(session)


def get_auth_service() -> AuthService:
    """Wire JWTService to the AuthService port.

    JWT_SECRET is read from env at request time; the default is only
    safe for local development and is rejected in production by env validation.
    """
    secret = os.environ.get("JWT_SECRET", _DEFAULT_JWT_SECRET)
    return JWTService(secret=secret, expiry_minutes=_JWT_EXPIRY_MINUTES)


@lru_cache(maxsize=1)
def get_email_sender() -> EmailSender:
    """Wire the configured email backend to the EmailSender port.

    Returns a cached singleton — email senders are stateless, so there is no
    need to recreate the (potentially expensive) boto3 client per request.
    Controlled by the EMAIL_BACKEND env var: 'ses' or 'stub' (default).
    """
    settings = get_settings()
    if settings.email_backend == "ses":
        from app.infrastructure.email.ses_email_sender import SESEmailSender

        assert settings.ses_from_email is not None  # guaranteed by Settings validator
        return SESEmailSender(
            from_email=settings.ses_from_email,
            region_name=settings.aws_default_region,
        )
    from app.infrastructure.email.email_sender_stub import EmailSenderStub

    return EmailSenderStub()
