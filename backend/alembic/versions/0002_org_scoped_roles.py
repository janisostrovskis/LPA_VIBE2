"""org-scoped roles — add id PK and organization_id FK to user_roles

Revision ID: 0002
Revises: 0001
Create Date: 2026-04-11 00:00:00.000000

Changes to user_roles:
  - Add ``id`` UUID PK (backfilled with gen_random_uuid())
  - Add ``organization_id`` UUID nullable FK → organizations.id ON DELETE CASCADE
  - Drop composite PK (user_id, role_name)
  - Promote ``id`` to sole PK
  - Add partial unique index for org-scoped roles (organization_id IS NOT NULL)
  - Add partial unique index for site-wide roles (organization_id IS NULL)
  - Add plain index on organization_id for FK lookups

Existing rows (site-wide "member" roles from registration) keep
organization_id = NULL and are covered by the site-wide partial index.
"""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add id column (nullable first so gen_random_uuid() can backfill rows).
    op.add_column(
        "user_roles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
            server_default=sa.text("gen_random_uuid()"),
        ),
    )
    # 2. Backfill id for all existing rows.
    op.execute("UPDATE user_roles SET id = gen_random_uuid() WHERE id IS NULL")
    # 3. Make id NOT NULL now that every row has a value.
    op.alter_column("user_roles", "id", nullable=False)

    # 4. Add organization_id column (nullable — site-wide roles use NULL).
    op.add_column(
        "user_roles",
        sa.Column(
            "organization_id",
            postgresql.UUID(as_uuid=True),
            nullable=True,
        ),
    )

    # 5. Drop the old composite PK.
    op.drop_constraint("user_roles_pkey", "user_roles", type_="primary")

    # 6. Promote id to the sole PK.
    op.create_primary_key("user_roles_pkey", "user_roles", ["id"])

    # 7. FK from organization_id → organizations.id ON DELETE CASCADE.
    op.create_foreign_key(
        "fk_user_roles_organization_id",
        "user_roles",
        "organizations",
        ["organization_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # 8. Partial unique index for org-scoped roles (organization_id IS NOT NULL).
    op.create_index(
        "uq_user_roles_scoped",
        "user_roles",
        ["user_id", "role_name", "organization_id"],
        unique=True,
        postgresql_where=sa.text("organization_id IS NOT NULL"),
    )

    # 9. Partial unique index for site-wide roles (organization_id IS NULL).
    op.create_index(
        "uq_user_roles_global",
        "user_roles",
        ["user_id", "role_name"],
        unique=True,
        postgresql_where=sa.text("organization_id IS NULL"),
    )

    # 10. Plain index on organization_id for FK lookups.
    op.create_index(
        "ix_user_roles_organization_id",
        "user_roles",
        ["organization_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_user_roles_organization_id", table_name="user_roles")
    op.drop_index("uq_user_roles_global", table_name="user_roles")
    op.drop_index("uq_user_roles_scoped", table_name="user_roles")
    op.drop_constraint(
        "fk_user_roles_organization_id", "user_roles", type_="foreignkey"
    )
    op.drop_constraint("user_roles_pkey", "user_roles", type_="primary")

    # Restore the composite PK.  The column pair is already NOT NULL because
    # user_id and role_name were always required.
    op.create_primary_key("user_roles_pkey", "user_roles", ["user_id", "role_name"])

    op.drop_column("user_roles", "organization_id")
    op.drop_column("user_roles", "id")
