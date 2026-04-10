"""initial accounts schema

Revision ID: 0001
Revises:
Create Date: 2026-04-10 00:00:00.000000

Creates the four tables that form the accounts aggregate:
  - users
  - organizations
  - user_roles
  - magic_link_tokens
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ------------------------------------------------------------------
    # users
    # ------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("email", sa.String(254), nullable=False),
        sa.Column("display_name", sa.String(200), nullable=False),
        sa.Column(
            "preferred_locale",
            sa.String(5),
            nullable=False,
            server_default="lv",
        ),
        sa.Column("password_hash", sa.String(255), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    # Case-insensitive uniqueness on email via functional index.
    op.create_index(
        "ix_users_email_lower",
        "users",
        [sa.text("lower(email)")],
        unique=True,
    )

    # ------------------------------------------------------------------
    # organizations
    # ------------------------------------------------------------------
    op.create_table(
        "organizations",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("legal_name", sa.String(300), nullable=False),
        sa.Column("registration_number", sa.String(50), nullable=False),
        sa.Column("vat_number", sa.String(50), nullable=True),
        sa.Column("address", sa.String(500), nullable=False),
        sa.Column("contact_email", sa.String(254), nullable=False),
        sa.Column("contact_person_name", sa.String(200), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("registration_number"),
    )

    # ------------------------------------------------------------------
    # user_roles
    # ------------------------------------------------------------------
    op.create_table(
        "user_roles",
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("role_name", sa.String(50), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "role_name"),
    )

    # ------------------------------------------------------------------
    # magic_link_tokens
    # ------------------------------------------------------------------
    op.create_table(
        "magic_link_tokens",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("token", sa.String(255), nullable=False),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "used",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )
    op.create_index(
        op.f("ix_magic_link_tokens_user_id"),
        "magic_link_tokens",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_magic_link_tokens_user_id"), table_name="magic_link_tokens"
    )
    op.drop_table("magic_link_tokens")
    op.drop_table("user_roles")
    op.drop_table("organizations")
    op.drop_index("ix_users_email_lower", table_name="users")
    op.drop_table("users")
