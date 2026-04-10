"""Port: abstract email sender."""

from __future__ import annotations

from abc import ABC, abstractmethod


class EmailSender(ABC):
    """Abstract service for sending emails. Concrete implementation ships in Phase 9."""

    @abstractmethod
    async def send(self, to: str, subject: str, body: str) -> None:
        """Send an email. Concrete implementation TBD (Phase 9)."""
        ...
