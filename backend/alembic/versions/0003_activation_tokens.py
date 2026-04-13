"""activation tokens — add purpose column to magic_link_tokens

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-11 00:00:00.000000

Changes to magic_link_tokens:
  - Add ``purpose`` VARCHAR(20) NOT NULL with server_default "login" so
    existing rows are backfilled as login tokens.
  - Add CHECK constraint ``ck_magic_link_tokens_purpose`` limiting values
    to 'login' and 'activation'.
  - Add partial index ``ix_magic_link_tokens_user_purpose_active`` on
    (user_id, purpose) WHERE used = false — used by the consume path to
    quickly locate unused tokens of a specific purpose for a given user.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add purpose column with a server_default so existing rows get "login".
    op.add_column(
        "magic_link_tokens",
        sa.Column(
            "purpose",
            sa.String(20),
            nullable=False,
            server_default="login",
        ),
    )

    # 2. CHECK constraint — only two valid purposes.
    op.create_check_constraint(
        "ck_magic_link_tokens_purpose",
        "magic_link_tokens",
        "purpose IN ('login', 'activation')",
    )

    # 3. Partial index on (user_id, purpose) for unused tokens.
    op.create_index(
        "ix_magic_link_tokens_user_purpose_active",
        "magic_link_tokens",
        ["user_id", "purpose"],
        unique=False,
        postgresql_where=sa.text("used = false"),
    )


def downgrade() -> None:
    # Reverse in opposite order: index → constraint → column.
    op.drop_index(
        "ix_magic_link_tokens_user_purpose_active",
        table_name="magic_link_tokens",
    )
    op.drop_constraint(
        "ck_magic_link_tokens_purpose",
        "magic_link_tokens",
        type_="check",
    )
    op.drop_column("magic_link_tokens", "purpose")
