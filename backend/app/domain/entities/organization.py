"""Organization domain entity — pure Python, no framework imports."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from uuid import UUID


@dataclass
class Organization:
    """An organization (studio or association) registered with LPA."""

    id: UUID
    legal_name: str
    registration_number: str
    vat_number: str | None
    address: str
    contact_email: str
    contact_person_name: str
    created_at: datetime
    updated_at: datetime
