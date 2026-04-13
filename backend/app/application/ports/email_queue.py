"""Port: EmailQueue — fire-and-forget enqueue of outbound email work."""

from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID


class EmailQueue(ABC):
    """Enqueue outbound email work for async processing by a worker.

    Implementations must be fire-and-forget and never raise on broker
    failures — log and return. Timing-sensitive flows (registration,
    resend-activation) depend on this method completing quickly regardless
    of whether the underlying email send will succeed.
    """

    @abstractmethod
    def enqueue_send_activation(
        self,
        *,
        user_id: UUID,
        email: str,
        locale: str,
        frontend_url: str,
        welcome: bool,
    ) -> None: ...
