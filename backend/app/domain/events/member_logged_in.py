"""Domain event emitted when a member successfully authenticates."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal
from uuid import UUID


@dataclass(frozen=True)
class MemberLoggedIn:
    member_id: UUID
    email: str
    logged_in_at: datetime
    method: Literal["password", "magic_link"]
