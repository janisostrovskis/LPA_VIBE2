"""SQLAlchemy ORM models for the accounts aggregate.

These are *infrastructure* classes — they are NOT domain entities.
Repositories map between these models and domain entities.

All primary keys are UUID v4.  All timestamps are UTC (server default via
``func.now()``; application code passes ``datetime.now(UTC)`` explicitly on
insert so the ORM value is consistent without a second SELECT).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Shared declarative base for all LPA ORM models."""


class UserModel(Base):
    """Persisted user account.  Maps to the ``users`` table."""

    __tablename__ = "users"
    __table_args__ = (
        # Case-insensitive uniqueness enforced at DB level via functional index.
        Index("ix_users_email_lower", func.lower("email"), unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(String(254), nullable=False)
    display_name: Mapped[str] = mapped_column(String(200), nullable=False)
    preferred_locale: Mapped[str] = mapped_column(
        String(5), nullable=False, server_default="lv"
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="true")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    roles: Mapped[list[UserRoleModel]] = relationship(
        "UserRoleModel", back_populates="user", cascade="all, delete-orphan"
    )
    magic_link_tokens: Mapped[list[MagicLinkTokenModel]] = relationship(
        "MagicLinkTokenModel", back_populates="user", cascade="all, delete-orphan"
    )


class OrganizationModel(Base):
    """Persisted organization (studio / association).  Maps to ``organizations``."""

    __tablename__ = "organizations"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    legal_name: Mapped[str] = mapped_column(String(300), nullable=False)
    registration_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    vat_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    address: Mapped[str] = mapped_column(String(500), nullable=False)
    contact_email: Mapped[str] = mapped_column(String(254), nullable=False)
    contact_person_name: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )


class UserRoleModel(Base):
    """Many-to-many: user ↔ role, optionally scoped to an organization.

    Maps to the ``user_roles`` table.

    Valid ``role_name`` values: "member", "org_admin", "content_editor",
    "reviewer", "site_admin".

    ``organization_id`` is NULL for site-wide roles (e.g. the "member" role
    assigned at registration) and non-NULL for org-scoped roles such as
    "org_admin" for a specific organization.
    """

    __tablename__ = "user_roles"
    __table_args__ = (
        # Org-scoped uniqueness: one role per user per org (WHERE org IS NOT NULL).
        # Both uniqueness constraints are partial indexes; SQLAlchemy UniqueConstraint
        # does not support WHERE clauses, so we use Index with unique=True throughout.
        Index(
            "uq_user_roles_scoped",
            "user_id",
            "role_name",
            "organization_id",
            unique=True,
            postgresql_where="organization_id IS NOT NULL",
        ),
        # Site-wide uniqueness: one global role per user (WHERE org IS NULL).
        Index(
            "uq_user_roles_global",
            "user_id",
            "role_name",
            unique=True,
            postgresql_where="organization_id IS NULL",
        ),
        Index("ix_user_roles_organization_id", "organization_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role_name: Mapped[str] = mapped_column(String(50), nullable=False)
    organization_id: Mapped[uuid.UUID | None] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=True,
    )

    user: Mapped[UserModel] = relationship("UserModel", back_populates="roles")


class MagicLinkTokenModel(Base):
    """Single-use authentication token sent via email.  Maps to ``magic_link_tokens``."""

    __tablename__ = "magic_link_tokens"

    id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    token: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    used: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    user: Mapped[UserModel] = relationship("UserModel", back_populates="magic_link_tokens")
