"""Email sender stub — logs instead of sending. Used in development and test environments."""

from __future__ import annotations

from app.application.ports.email_sender import EmailSender
from app.lib.logger import get_logger

_logger = get_logger(__name__)


class EmailSenderStub(EmailSender):
    """Stub EmailSender that logs email content instead of delivering it."""

    async def send(
        self, to: str, subject: str, body: str, html_body: str | None = None
    ) -> None:
        _logger.info(
            "Email stub — would send email",
            extra={"to": to, "subject": subject, "body_preview": body[:200]},
        )
