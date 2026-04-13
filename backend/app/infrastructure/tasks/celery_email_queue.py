"""CeleryEmailQueue — EmailQueue port implemented via Celery."""

from __future__ import annotations

from uuid import UUID

from app.application.ports.email_queue import EmailQueue
from app.lib.logger import get_logger

logger = get_logger(__name__)


class CeleryEmailQueue(EmailQueue):
    """Enqueue activation emails via Celery's .delay() call.

    Catches broker-level failures and logs a WARNING instead of raising,
    so registration succeeds even when Redis is temporarily unavailable.
    """

    def enqueue_send_activation(
        self,
        *,
        user_id: UUID,
        email: str,
        locale: str,
        frontend_url: str,
        welcome: bool,
    ) -> None:
        from app.infrastructure.tasks.email_tasks import send_activation_email_task

        try:
            send_activation_email_task.delay(
                str(user_id),
                email,
                locale,
                frontend_url,
                welcome,
            )
        # FAIL-QUIET-EXCEPTION: broker outage must not block signup. Registration
        # UX is prioritised over email delivery reliability; a missed email is
        # recoverable via /resend-activation, a 500 on /register is not. Warning
        # log carries user_id and email for operator alerting on broker loss.
        except Exception as exc:  # noqa: BLE001
            logger.warning(
                "Failed to enqueue activation email; continuing without email",
                extra={"user_id": str(user_id), "email": email, "error": str(exc)},
            )
