"""Member domain entity — pure Python, no framework imports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID

from app.domain.value_objects.locale import Locale


@dataclass
class Member:
    """An individual LPA member (user account).

    ``password_hash`` is ``None`` for magic-link-only users who have never
    set a password.
    """

    id: UUID
    email: str  # stored lowercase; validated via Email VO before construction
    display_name: str
    preferred_locale: Locale
    password_hash: str | None  # None for magic-link-only users
    is_active: bool
    created_at: datetime
    updated_at: datetime
