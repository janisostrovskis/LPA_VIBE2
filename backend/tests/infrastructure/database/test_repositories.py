"""Unit tests for repository mapping logic and ABC conformance.

These tests verify round-trip fidelity between domain entities and ORM model
fields, and that concrete repository classes properly implement their ABCs.
No live database connection is required.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

import pytest

from app.domain.entities.member import Member
from app.domain.entities.organization import Organization
from app.domain.value_objects.locale import Locale
from app.infrastructure.database.models import OrganizationModel, UserModel
from app.infrastructure.database.repositories.magic_link_repository import (
    SqlaMagicLinkRepository,
)
from app.infrastructure.database.repositories.member_repository import (
    SqlaMemberRepository,
    _entity_to_model,
    _model_to_entity,
)
from app.infrastructure.database.repositories.organization_repository import (
    SqlaOrganizationRepository,
    _entity_to_model as org_entity_to_model,
    _model_to_entity as org_model_to_entity,
)

_MEMBER_ID = UUID("00000000-0000-0000-0000-000000000001")
_ORG_ID = UUID("00000000-0000-0000-0000-000000000002")
_NOW = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)


def _make_member() -> Member:
    return Member(
        id=_MEMBER_ID,
        email="test@example.com",
        display_name="Test User",
        preferred_locale=Locale.LV,
        password_hash=None,
        is_active=True,
        created_at=_NOW,
        updated_at=_NOW,
    )


def _make_org() -> Organization:
    return Organization(
        id=_ORG_ID,
        legal_name="Test Studio SIA",
        registration_number="40001234567",
        vat_number="LV40001234567",
        address="Riga, Latvia",
        contact_email="studio@example.com",
        contact_person_name="Jane Doe",
        created_at=_NOW,
        updated_at=_NOW,
    )


class TestMemberRoundTrip:
    def test_entity_to_model_fields(self) -> None:
        member = _make_member()
        model = _entity_to_model(member)
        assert model.id == member.id
        assert model.email == member.email
        assert model.display_name == member.display_name
        assert model.preferred_locale == "lv"
        assert model.password_hash is None
        assert model.is_active is True

    def test_model_to_entity_fields(self) -> None:
        model = UserModel(
            id=_MEMBER_ID,
            email="test@example.com",
            display_name="Test User",
            preferred_locale="lv",
            password_hash=None,
            is_active=True,
            created_at=_NOW,
            updated_at=_NOW,
        )
        member = _model_to_entity(model)
        assert member.id == _MEMBER_ID
        assert member.email == "test@example.com"
        assert member.preferred_locale is Locale.LV
        assert member.password_hash is None
        assert member.is_active is True

    def test_round_trip_fidelity(self) -> None:
        original = _make_member()
        recovered = _model_to_entity(_entity_to_model(original))
        assert recovered.id == original.id
        assert recovered.email == original.email
        assert recovered.display_name == original.display_name
        assert recovered.preferred_locale == original.preferred_locale
        assert recovered.password_hash == original.password_hash
        assert recovered.is_active == original.is_active
        assert recovered.created_at == original.created_at
        assert recovered.updated_at == original.updated_at

    @pytest.mark.parametrize("locale", list(Locale))
    def test_all_locales_round_trip(self, locale: Locale) -> None:
        member = Member(
            id=_MEMBER_ID,
            email="x@x.com",
            display_name="X",
            preferred_locale=locale,
            password_hash=None,
            is_active=True,
            created_at=_NOW,
            updated_at=_NOW,
        )
        recovered = _model_to_entity(_entity_to_model(member))
        assert recovered.preferred_locale is locale

    def test_password_hash_preserved(self) -> None:
        member = Member(
            id=_MEMBER_ID,
            email="x@x.com",
            display_name="X",
            preferred_locale=Locale.EN,
            password_hash="$argon2id$...",
            is_active=True,
            created_at=_NOW,
            updated_at=_NOW,
        )
        recovered = _model_to_entity(_entity_to_model(member))
        assert recovered.password_hash == "$argon2id$..."


class TestOrganizationRoundTrip:
    def test_entity_to_model_fields(self) -> None:
        org = _make_org()
        model = org_entity_to_model(org)
        assert model.id == org.id
        assert model.legal_name == org.legal_name
        assert model.registration_number == org.registration_number
        assert model.vat_number == org.vat_number
        assert model.address == org.address
        assert model.contact_email == org.contact_email
        assert model.contact_person_name == org.contact_person_name

    def test_model_to_entity_fields(self) -> None:
        model = OrganizationModel(
            id=_ORG_ID,
            legal_name="Test Studio SIA",
            registration_number="40001234567",
            vat_number=None,
            address="Riga, Latvia",
            contact_email="studio@example.com",
            contact_person_name="Jane Doe",
            created_at=_NOW,
            updated_at=_NOW,
        )
        org = org_model_to_entity(model)
        assert org.id == _ORG_ID
        assert org.vat_number is None

    def test_round_trip_fidelity(self) -> None:
        original = _make_org()
        recovered = org_model_to_entity(org_entity_to_model(original))
        assert recovered.id == original.id
        assert recovered.legal_name == original.legal_name
        assert recovered.registration_number == original.registration_number
        assert recovered.vat_number == original.vat_number
        assert recovered.address == original.address
        assert recovered.contact_email == original.contact_email
        assert recovered.contact_person_name == original.contact_person_name
        assert recovered.created_at == original.created_at
        assert recovered.updated_at == original.updated_at

    def test_vat_number_none_preserved(self) -> None:
        org = Organization(
            id=_ORG_ID,
            legal_name="X",
            registration_number="Y",
            vat_number=None,
            address="Z",
            contact_email="a@b.com",
            contact_person_name="Name",
            created_at=_NOW,
            updated_at=_NOW,
        )
        recovered = org_model_to_entity(org_entity_to_model(org))
        assert recovered.vat_number is None


class TestRepositoryAbstractConformance:
    def test_sqla_member_repository_is_concrete(self) -> None:
        from app.application.ports.member_repository import MemberRepository

        assert issubclass(SqlaMemberRepository, MemberRepository)

    def test_sqla_organization_repository_is_concrete(self) -> None:
        from app.application.ports.organization_repository import OrganizationRepository

        assert issubclass(SqlaOrganizationRepository, OrganizationRepository)

    def test_sqla_magic_link_repository_is_concrete(self) -> None:
        from app.application.ports.magic_link_repository import MagicLinkRepository

        assert issubclass(SqlaMagicLinkRepository, MagicLinkRepository)
