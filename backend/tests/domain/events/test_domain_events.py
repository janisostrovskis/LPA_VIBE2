"""Tests for domain events MemberRegistered and MemberLoggedIn."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest
from app.domain.events.member_logged_in import MemberLoggedIn
from app.domain.events.member_registered import MemberRegistered


class TestMemberRegistered:
    def _make(self, **kwargs: object) -> MemberRegistered:
        defaults: dict[str, object] = {
            "member_id": uuid4(),
            "email": "test@example.com",
            "registered_at": datetime.now(tz=UTC),
        }
        defaults.update(kwargs)
        return MemberRegistered(**defaults)  # type: ignore[arg-type]

    def test_fields_accessible(self) -> None:
        uid = uuid4()
        ts = datetime(2026, 1, 1, tzinfo=UTC)
        event = MemberRegistered(
            member_id=uid,
            email="a@b.com",
            registered_at=ts,
        )
        assert event.member_id == uid
        assert event.email == "a@b.com"
        assert event.registered_at == ts

    def test_member_id_is_uuid(self) -> None:
        event = self._make()
        assert isinstance(event.member_id, UUID)

    def test_frozen(self) -> None:
        event = self._make()
        with pytest.raises((AttributeError, TypeError)):
            event.email = "other@example.com"  # type: ignore[misc]


class TestMemberLoggedIn:
    def _make(self, **kwargs: object) -> MemberLoggedIn:
        defaults: dict[str, object] = {
            "member_id": uuid4(),
            "email": "test@example.com",
            "logged_in_at": datetime.now(tz=UTC),
            "method": "password",
        }
        defaults.update(kwargs)
        return MemberLoggedIn(**defaults)  # type: ignore[arg-type]

    def test_fields_accessible(self) -> None:
        uid = uuid4()
        ts = datetime(2026, 1, 1, tzinfo=UTC)
        event = MemberLoggedIn(
            member_id=uid,
            email="a@b.com",
            logged_in_at=ts,
            method="magic_link",
        )
        assert event.member_id == uid
        assert event.email == "a@b.com"
        assert event.logged_in_at == ts
        assert event.method == "magic_link"

    def test_method_password(self) -> None:
        event = self._make(method="password")
        assert event.method == "password"

    def test_method_magic_link(self) -> None:
        event = self._make(method="magic_link")
        assert event.method == "magic_link"

    def test_frozen(self) -> None:
        event = self._make()
        with pytest.raises((AttributeError, TypeError)):
            event.method = "other"  # type: ignore[misc]
