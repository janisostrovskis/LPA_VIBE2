"""Tests for app.lib.errors — domain error taxonomy."""

from app.lib.errors import (
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)


def test_not_found_code() -> None:
    assert NotFoundError(message="user").code == "not_found"


def test_validation_error_code() -> None:
    assert ValidationError(message="bad input").code == "validation_error"


def test_conflict_error_code() -> None:
    assert ConflictError(message="duplicate").code == "conflict"


def test_unauthorized_error_code() -> None:
    assert UnauthorizedError(message="no token").code == "unauthorized"


def test_forbidden_error_code() -> None:
    assert ForbiddenError(message="no access").code == "forbidden"


def test_domain_error_code() -> None:
    assert DomainError(message="generic").code == "domain_error"


def test_details_populated() -> None:
    err = DomainError(message="x", details={"k": 1})
    assert err.details == {"k": 1}


def test_details_defaults_to_none() -> None:
    err = DomainError(message="x")
    assert err.details is None


def test_equality() -> None:
    assert NotFoundError(message="u") == NotFoundError(message="u")


def test_inequality_different_message() -> None:
    assert NotFoundError(message="a") != NotFoundError(message="b")


def test_subclass_of_domain_error() -> None:
    assert isinstance(NotFoundError(message="u"), DomainError)


def test_all_subclasses_are_domain_errors() -> None:
    errors = [
        ValidationError(message="v"),
        ConflictError(message="c"),
        UnauthorizedError(message="u"),
        ForbiddenError(message="f"),
    ]
    for err in errors:
        assert isinstance(err, DomainError)
