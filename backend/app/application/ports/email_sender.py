"""Port: abstract email sender."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmailSender(ABC):
    """Abstract service for sending emails. Concrete implementation ships in Phase 9."""

    @abstractmethod
    async def send(
        self, to: str, subject: str, body: str, html_body: str | None = None
    ) -> None:
        """Send an email.

        Args:
            to: Recipient email address.
            subject: Email subject line.
            body: Plain-text email body.
            html_body: Optional HTML body. When provided, a multipart message is sent.
        """
        ...
