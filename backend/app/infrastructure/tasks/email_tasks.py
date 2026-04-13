"""Celery tasks for email delivery.

Tasks in this module run inside the worker process (or eagerly in-thread
during tests / soft-rollback mode). Each task opens its own DB session
via build_worker_sessionmaker() so it is fully independent of the
FastAPI request session.
"""

from __future__ import annotations

import asyncio
import os
from typing import Any
from uuid import UUID

from app.infrastructure.tasks.celery_app import app
from app.lib.logger import get_logger

logger = get_logger(__name__)


async def _run_send_activation(
    user_id_str: str,
    email: str,
    locale: str,
    frontend_url: str,
    welcome: bool,
) -> None:
    """Inner async impl called by the task via asyncio.run()."""
    from app.application.ports.email_sender import EmailSender
    from app.application.services.activation_email import send_activation_email
    from app.infrastructure.database.repositories.magic_link_repository import (
        SqlaMagicLinkRepository,
    )
    from app.infrastructure.tasks.session import build_worker_sessionmaker

    session_factory = build_worker_sessionmaker()
    async with session_factory() as session:
        magic_link_repo = SqlaMagicLinkRepository(session)
        email_sender = _build_email_sender()

        await send_activation_email(
            magic_link_repo=magic_link_repo,
            email_sender=email_sender,
            user_id=UUID(user_id_str),
            email=email,
            locale=locale,
            frontend_url=frontend_url,
            welcome=welcome,
        )
        await session.commit()

    logger.info(
        "send_activation_email_task completed",
        extra={"user_id": user_id_str, "welcome": welcome},
    )


def _build_email_sender() -> Any:
    """Construct an EmailSender for the worker process.

    Mirrors the logic in get_email_sender() in dependencies.py but does
    not import FastAPI so the worker boot stays light.
    """
    email_backend = os.environ.get("EMAIL_BACKEND", "stub")
    if email_backend == "ses":
        from app.infrastructure.email.ses_email_sender import SESEmailSender

        ses_from_email = os.environ.get("SES_FROM_EMAIL", "")
        aws_region = os.environ.get("AWS_DEFAULT_REGION", "eu-north-1")
        return SESEmailSender(from_email=ses_from_email, region_name=aws_region)

    from app.infrastructure.email.email_sender_stub import EmailSenderStub

    return EmailSenderStub()


@app.task(
    bind=True,
    autoretry_for=(ConnectionError, OSError),
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=60,
    retry_jitter=True,
)
def send_activation_email_task(
    self: Any,
    user_id_str: str,
    email: str,
    locale: str,
    frontend_url: str,
    welcome: bool,
) -> None:
    """Send an activation email from within the Celery worker.

    Signature uses plain JSON-serialisable types (str, bool) because
    Celery uses JSON serialization by default.
    """
    logger.info(
        "send_activation_email_task started",
        extra={"user_id": user_id_str, "retry": self.request.retries},
    )
    asyncio.run(
        _run_send_activation(
            user_id_str=user_id_str,
            email=email,
            locale=locale,
            frontend_url=frontend_url,
            welcome=welcome,
        )
    )
