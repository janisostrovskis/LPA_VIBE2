"""Locale value object — supported UI/content locales for the LPA platform."""

from __future__ import annotations

from enum import StrEnum


class Locale(StrEnum):
    """Supported locales.  LV is the primary locale for Latvia."""

    LV = "lv"
    EN = "en"
    RU = "ru"
