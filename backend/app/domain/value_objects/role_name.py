"""Value object: valid role names for the LPA platform."""

from __future__ import annotations

from enum import StrEnum


class RoleName(StrEnum):
    """Valid role_name values for the user_roles table."""

    MEMBER = "member"
    ORG_ADMIN = "org_admin"
    CONTENT_EDITOR = "content_editor"
    REVIEWER = "reviewer"
    SITE_ADMIN = "site_admin"
