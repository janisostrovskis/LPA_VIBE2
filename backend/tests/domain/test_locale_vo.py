"""Tests for the Locale value object."""

import pytest

from app.domain.value_objects.locale import Locale


class TestLocaleValues:
    def test_lv_value(self) -> None:
        assert Locale.LV == "lv"

    def test_en_value(self) -> None:
        assert Locale.EN == "en"

    def test_ru_value(self) -> None:
        assert Locale.RU == "ru"

    def test_all_three_members_exist(self) -> None:
        members = list(Locale)
        assert len(members) == 3


class TestLocaleStrEnum:
    def test_is_str(self) -> None:
        assert isinstance(Locale.LV, str)

    def test_membership_by_value(self) -> None:
        assert Locale("lv") is Locale.LV
        assert Locale("en") is Locale.EN
        assert Locale("ru") is Locale.RU

    def test_invalid_value_raises(self) -> None:
        with pytest.raises(ValueError):
            Locale("de")

    def test_string_comparison(self) -> None:
        assert Locale.LV == "lv"
        assert Locale.EN == "en"
        assert Locale.RU == "ru"
