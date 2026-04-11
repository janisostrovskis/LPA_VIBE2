"""SQLAlchemy implementation of MemberRepository."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import exists, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.ports.member_repository import MemberRepository
from app.domain.entities.member import Member
from app.domain.value_objects.locale import Locale
from app.domain.value_objects.role_name import RoleName
from app.infrastructure.database.models import UserModel, UserRoleModel


def _model_to_entity(model: UserModel) -> Member:
    return Member(
        id=model.id,
        email=model.email,
        display_name=model.display_name,
        preferred_locale=Locale(model.preferred_locale),
        password_hash=model.password_hash,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def _entity_to_model(member: Member) -> UserModel:
    return UserModel(
        id=member.id,
        email=member.email,
        display_name=member.display_name,
        preferred_locale=str(member.preferred_locale),
        password_hash=member.password_hash,
        is_active=member.is_active,
        created_at=member.created_at,
        updated_at=member.updated_at,
    )


class SqlaMemberRepository(MemberRepository):
    """Concrete MemberRepository backed by an AsyncSession."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, member: Member) -> Member:
        model = _entity_to_model(member)
        self._session.add(model)
        role = UserRoleModel(user_id=member.id, role_name=RoleName.MEMBER, organization_id=None)
        self._session.add(role)
        await self._session.flush()
        return _model_to_entity(model)

    async def get_by_id(self, member_id: UUID) -> Member | None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == member_id)
        )
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model is not None else None

    async def get_by_email(self, email: str) -> Member | None:
        result = await self._session.execute(
            select(UserModel).where(
                func.lower(UserModel.email) == email.lower()
            )
        )
        model = result.scalar_one_or_none()
        return _model_to_entity(model) if model is not None else None

    async def update(self, member: Member) -> Member:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == member.id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            from app.lib.errors import NotFoundError

            raise NotFoundError(message=f"Member {member.id} not found")  # type: ignore[misc]
        model.email = member.email
        model.display_name = member.display_name
        model.preferred_locale = str(member.preferred_locale)
        model.password_hash = member.password_hash
        model.is_active = member.is_active
        model.updated_at = member.updated_at
        await self._session.flush()
        return _model_to_entity(model)

    async def delete(self, member_id: UUID) -> None:
        result = await self._session.execute(
            select(UserModel).where(UserModel.id == member_id)
        )
        model = result.scalar_one_or_none()
        if model is None:
            from app.lib.errors import NotFoundError

            raise NotFoundError(message=f"Member {member_id} not found")  # type: ignore[misc]
        await self._session.delete(model)
        await self._session.flush()

    async def has_org_role(self, user_id: UUID, org_id: UUID, role_name: RoleName) -> bool:
        result = await self._session.execute(
            select(
                exists().where(
                    UserRoleModel.user_id == user_id,
                    UserRoleModel.organization_id == org_id,
                    UserRoleModel.role_name == role_name,
                )
            )
        )
        return bool(result.scalar())

    async def assign_org_role(self, user_id: UUID, org_id: UUID, role_name: RoleName) -> None:
        role = UserRoleModel(
            user_id=user_id,
            organization_id=org_id,
            role_name=role_name,
        )
        self._session.add(role)
        await self._session.flush()
