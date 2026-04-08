"""Tests for app.lib.result — Result[T, E] sum type."""

import pytest
from app.lib.result import Err, Ok, Result  # noqa: F401 — Result used as annotation


def test_ok_value() -> None:
    assert Ok(42).value == 42


def test_ok_is_ok() -> None:
    assert Ok(42).is_ok is True


def test_err_error() -> None:
    assert Err("boom").error == "boom"


def test_err_is_ok() -> None:
    assert Err("boom").is_ok is False


def test_ok_equality() -> None:
    assert Ok(1) == Ok(1)


def test_ok_inequality_different_value() -> None:
    assert Ok(1) != Ok(2)


def test_ok_inequality_vs_err() -> None:
    assert Ok(1) != Err(1)


def test_pattern_match_ok() -> None:
    r: Result[int, str] = Ok(7)
    matched: int | None = None
    match r:
        case Ok(value=v):
            matched = v
        case Err():
            matched = None
    assert matched == 7


def test_pattern_match_err() -> None:
    r: Result[int, str] = Err("fail")
    matched: str | None = None
    match r:
        case Ok():
            matched = None
        case Err(error=e):
            matched = e
    assert matched == "fail"


def test_ok_immutability() -> None:
    ok = Ok(1)
    with pytest.raises((AttributeError, TypeError)):
        ok.value = 2  # type: ignore[misc]


def test_err_immutability() -> None:
    err = Err("x")
    with pytest.raises((AttributeError, TypeError)):
        err.error = "y"  # type: ignore[misc]


def unwrap(r: Result[int, str]) -> int:
    if isinstance(r, Ok):
        return r.value
    raise ValueError(r.error)


def test_generic_reuse_ok() -> None:
    assert unwrap(Ok(99)) == 99


def test_generic_reuse_err() -> None:
    with pytest.raises(ValueError, match="oops"):
        unwrap(Err("oops"))
