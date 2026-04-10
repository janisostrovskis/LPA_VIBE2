"""COLA domain layer — value objects (immutable, equality-by-value)."""

from app.domain.value_objects.email import Email
from app.domain.value_objects.locale import Locale

__all__ = ["Email", "Locale"]
