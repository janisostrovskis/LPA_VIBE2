"""Email value object — immutable, validated, normalized to lowercase."""

from __future__ import annotations

import re
from dataclasses import dataclass

# Permissive regex: local@domain.tld  — rejects obviously malformed addresses
# without being RFC-5321 strict.  Deliberately simple so legitimate addresses
# are never rejected.
_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$",
)


@dataclass(frozen=True)
class Email:
    """Validated, normalized e-mail address.

    Always lowercase.  Construct via ``Email.create()`` — do not call the
    dataclass constructor directly with raw user input.
    """

    value: str

    @classmethod
    def create(cls, raw: str) -> Email:
        """Validate *raw*, normalize to lowercase, and return an ``Email``.

        Raises ``ValueError`` if *raw* does not match the expected format.
        Value objects raise standard Python exceptions; use-case layers wrap
        these in ``Result[T, ValidationError]`` for structured error handling.
        """
        normalized = raw.strip().lower()
        if not _EMAIL_RE.match(normalized):
            raise ValueError(f"Invalid email address: {raw!r}")
        return cls(value=normalized)

    def __str__(self) -> str:
        return self.value
