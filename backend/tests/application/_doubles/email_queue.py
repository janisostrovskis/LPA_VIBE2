"""Test double: FakeEmailQueue."""

from __future__ import annotations

from uuid import UUID

from app.application.ports.email_queue import EmailQueue


class FakeEmailQueue(EmailQueue):
    """In-memory test double that records all enqueue calls."""

    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def enqueue_send_activation(
        self,
        *,
        user_id: UUID,
        email: str,
        locale: str,
        frontend_url: str,
        welcome: bool,
    ) -> None:
        self.calls.append(
            {
                "user_id": user_id,
                "email": email,
                "locale": locale,
                "frontend_url": frontend_url,
                "welcome": welcome,
            }
        )
