"""Tests for app.infrastructure.config.env."""
import pytest
from app.infrastructure.config import Environment, LogLevel, Settings, get_settings
from pydantic import ValidationError

# Test fixtures. Not real credentials.
_URL = "postgresql://x:y@db:5432/z"  # pragma: allowlist secret
_URL_A = "postgresql://a:a@db:5432/a"  # pragma: allowlist secret
_URL_B = "postgresql://b:b@db:5432/b"  # pragma: allowlist secret


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip relevant env vars and clear the get_settings cache around each test."""
    for var in ("DATABASE_URL", "BACKEND_PORT", "ENVIRONMENT", "LPA_LOG_LEVEL"):
        monkeypatch.delenv(var, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_missing_database_url_raises() -> None:
    with pytest.raises(ValidationError) as exc_info:
        Settings()  # type: ignore[call-arg]
    message = str(exc_info.value)
    assert "database_url" in message.lower() or "DATABASE_URL" in message


def test_database_url_required_value(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    assert get_settings().database_url == _URL


def test_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    settings = get_settings()
    assert settings.backend_port == 8000
    assert settings.environment is Environment.DEVELOPMENT
    assert settings.log_level is LogLevel.INFO


def test_backend_port_too_high(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("BACKEND_PORT", "99999")
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_backend_port_zero(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("BACKEND_PORT", "0")
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_environment_production(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("ENVIRONMENT", "production")
    assert get_settings().environment is Environment.PRODUCTION


def test_environment_invalid(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("ENVIRONMENT", "bogus")
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_log_level_debug_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("LPA_LOG_LEVEL", "DEBUG")
    assert get_settings().log_level is LogLevel.DEBUG


def test_lru_cache_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    first = get_settings()
    second = get_settings()
    assert first is second


def test_cache_clear_refreshes(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL_A)
    first = get_settings()
    assert first.database_url == _URL_A
    monkeypatch.setenv("DATABASE_URL", _URL_B)
    cached = get_settings()
    assert cached.database_url == _URL_A
    get_settings.cache_clear()
    refreshed = get_settings()
    assert refreshed.database_url == _URL_B


def test_extra_env_vars_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("UNRELATED_VAR", "foo")
    Settings()  # type: ignore[call-arg]
