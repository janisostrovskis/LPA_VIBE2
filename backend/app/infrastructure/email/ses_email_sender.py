"""Amazon SES implementation of the EmailSender port."""

from __future__ import annotations

import asyncio
from typing import Any

import boto3

from app.application.ports.email_sender import EmailSender


class SESEmailSender(EmailSender):
    """Send emails via Amazon SES using boto3."""

    def __init__(self, from_email: str, region_name: str) -> None:
        self._from_email = from_email
        self._client: Any = boto3.client("ses", region_name=region_name)

    async def send(
        self, to: str, subject: str, body: str, html_body: str | None = None
    ) -> None:
        """Send an email via SES, offloading the blocking boto3 call to a thread."""
        await asyncio.to_thread(self._send_sync, to, subject, body, html_body)

    def _send_sync(
        self, to: str, subject: str, body: str, html_body: str | None
    ) -> None:
        body_payload: dict[str, Any] = {
            "Text": {"Data": body, "Charset": "UTF-8"},
        }
        if html_body is not None:
            body_payload["Html"] = {"Data": html_body, "Charset": "UTF-8"}

        self._client.send_email(
            Source=self._from_email,
            Destination={"ToAddresses": [to]},
            Message={
                "Subject": {"Data": subject, "Charset": "UTF-8"},
                "Body": body_payload,
            },
        )
