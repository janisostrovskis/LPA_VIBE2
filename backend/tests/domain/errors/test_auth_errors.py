"""Tests for typed authentication domain errors."""

from __future__ import annotations

import pytest
from app.domain.errors.auth_error import (
    EmailAlreadyRegisteredError,
    InsufficientRoleError,
    InvalidCredentialsError,
    MagicLinkExpiredError,
    WeakPasswordError,
)
from app.lib.errors import (
    ConflictError,
    DomainError,
    ForbiddenError,
    UnauthorizedError,
    ValidationError,
)


class TestInvalidCredentialsError:
    def test_code(self) -> None:
        assert InvalidCredentialsError.code == "invalid_credentials"

    def test_inherits_unauthorized(self) -> None:
        assert issubclass(InvalidCredentialsError, UnauthorizedError)
        assert issubclass(InvalidCredentialsError, DomainError)

    def test_message(self) -> None:
        err = InvalidCredentialsError(message="Bad credentials")
        assert err.message == "Bad credentials"

    def test_frozen(self) -> None:
        err = InvalidCredentialsError(message="x")
        with pytest.raises((AttributeError, TypeError)):
            err.message = "y"  # type: ignore[misc]


class TestEmailAlreadyRegisteredError:
    def test_code(self) -> None:
        assert EmailAlreadyRegisteredError.code == "email_already_registered"

    def test_inherits_conflict(self) -> None:
        assert issubclass(EmailAlreadyRegisteredError, ConflictError)
        assert issubclass(EmailAlreadyRegisteredError, DomainError)

    def test_message(self) -> None:
        err = EmailAlreadyRegisteredError(message="Already exists")
        assert err.message == "Already exists"

    def test_frozen(self) -> None:
        err = EmailAlreadyRegisteredError(message="x")
        with pytest.raises((AttributeError, TypeError)):
            err.message = "y"  # type: ignore[misc]


class TestMagicLinkExpiredError:
    def test_code(self) -> None:
        assert MagicLinkExpiredError.code == "magic_link_expired"

    def test_inherits_validation(self) -> None:
        assert issubclass(MagicLinkExpiredError, ValidationError)
        assert issubclass(MagicLinkExpiredError, DomainError)

    def test_message(self) -> None:
        err = MagicLinkExpiredError(message="Link expired")
        assert err.message == "Link expired"

    def test_frozen(self) -> None:
        err = MagicLinkExpiredError(message="x")
        with pytest.raises((AttributeError, TypeError)):
            err.message = "y"  # type: ignore[misc]


class TestInsufficientRoleError:
    def test_code(self) -> None:
        assert InsufficientRoleError.code == "insufficient_role"

    def test_inherits_forbidden(self) -> None:
        assert issubclass(InsufficientRoleError, ForbiddenError)
        assert issubclass(InsufficientRoleError, DomainError)

    def test_message(self) -> None:
        err = InsufficientRoleError(message="Access denied")
        assert err.message == "Access denied"

    def test_frozen(self) -> None:
        err = InsufficientRoleError(message="x")
        with pytest.raises((AttributeError, TypeError)):
            err.message = "y"  # type: ignore[misc]


class TestWeakPasswordError:
    def test_code(self) -> None:
        assert WeakPasswordError.code == "weak_password"

    def test_inherits_validation(self) -> None:
        assert issubclass(WeakPasswordError, ValidationError)
        assert issubclass(WeakPasswordError, DomainError)

    def test_message(self) -> None:
        err = WeakPasswordError(message="Password too weak")
        assert err.message == "Password too weak"

    def test_frozen(self) -> None:
        err = WeakPasswordError(message="x")
        with pytest.raises((AttributeError, TypeError)):
            err.message = "y"  # type: ignore[misc]
