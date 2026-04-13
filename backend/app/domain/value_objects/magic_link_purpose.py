"""Value object: purpose of a magic-link token."""

from __future__ import annotations

from enum import StrEnum


class MagicLinkPurpose(StrEnum):
    """Valid purpose values for magic_link_tokens rows.

    The DB CHECK constraint on ``magic_link_tokens.purpose`` must stay in sync
    with this enum (see alembic migration 0003).
    """

    LOGIN = "login"
    ACTIVATION = "activation"
