"""Shared helper: generate an activation token and send the activation email.

Both ``RegisterMember`` and ``ResendActivation`` build the same token and
email body; this helper is the single source of truth so the two flows
cannot drift apart.
"""

from __future__ import annotations

import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from app.application.ports.email_sender import EmailSender
from app.application.ports.magic_link_repository import MagicLinkRepository
from app.domain.value_objects.magic_link_purpose import MagicLinkPurpose

ACTIVATION_TOKEN_TTL_HOURS = 24


async def send_activation_email(
    *,
    magic_link_repo: MagicLinkRepository,
    email_sender: EmailSender,
    user_id: UUID,
    email: str,
    locale: str,
    frontend_url: str,
    welcome: bool = False,
) -> None:
    """Create an activation token, persist it, and send the activation email.

    Raises whatever the underlying repository or email sender raises — the
    caller is responsible for transactional boundaries.
    """
    # Invalidate any prior unused activation tokens for this user so only the
    # freshest link is live. Closes the stale-token window after resends.
    await magic_link_repo.invalidate_unused_for_user(
        user_id, purpose=MagicLinkPurpose.ACTIVATION
    )

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(tz=UTC) + timedelta(hours=ACTIVATION_TOKEN_TTL_HOURS)
    await magic_link_repo.create(
        token, user_id, expires_at, purpose=MagicLinkPurpose.ACTIVATION
    )

    activation_url = f"{frontend_url}/{locale}/activate?token={token}"
    intro = "Welcome to LPA!\n\n" if welcome else ""
    body = (
        f"{intro}"
        f"Click this link to activate your account:\n{activation_url}\n\n"
        f"This link expires in {ACTIVATION_TOKEN_TTL_HOURS} hours."
    )
    await email_sender.send(
        to=email,
        subject="Activate your LPA account",
        body=body,
    )
