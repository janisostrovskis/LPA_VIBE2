"""Tests for rate-limit and queue settings fields in app.infrastructure.config.env."""
import pytest
from app.infrastructure.config import Settings, get_settings
from pydantic import ValidationError

_URL = "postgresql://x:y@db:5432/z"  # pragma: allowlist secret


@pytest.fixture(autouse=True)
def _isolate_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Strip relevant env vars and clear the get_settings cache around each test."""
    for var in (
        "DATABASE_URL",
        "ENVIRONMENT",
        "REDIS_URL",
        "CELERY_BROKER_URL",
        "RATE_LIMIT_REDIS_URL",
        "RATE_LIMIT_ENABLED",
        "TRUSTED_PROXY_HOPS",
    ):
        monkeypatch.delenv(var, raising=False)
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_rate_limit_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    settings = Settings()  # type: ignore[call-arg]
    assert settings.redis_url == "redis://redis:6379/0"
    assert settings.celery_broker_url == "redis://redis:6379/0"
    assert settings.rate_limit_redis_url == "redis://redis:6379/1"
    assert settings.rate_limit_enabled is True
    assert settings.trusted_proxy_hops == 0


def test_rate_limit_enabled_false_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    settings = Settings()  # type: ignore[call-arg]
    assert settings.rate_limit_enabled is False


def test_redis_url_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("REDIS_URL", "redis://other:6380/2")
    settings = Settings()  # type: ignore[call-arg]
    assert settings.redis_url == "redis://other:6380/2"


def test_rate_limit_redis_url_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("RATE_LIMIT_REDIS_URL", "redis://ratelimit:6379/5")
    settings = Settings()  # type: ignore[call-arg]
    assert settings.rate_limit_redis_url == "redis://ratelimit:6379/5"


def test_trusted_proxy_hops_negative_rejected(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("TRUSTED_PROXY_HOPS", "-1")
    with pytest.raises(ValidationError):
        Settings()  # type: ignore[call-arg]


def test_trusted_proxy_hops_positive(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("TRUSTED_PROXY_HOPS", "2")
    settings = Settings()  # type: ignore[call-arg]
    assert settings.trusted_proxy_hops == 2


def test_prod_requires_rate_limit_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    with pytest.raises(ValidationError) as exc_info:
        Settings()  # type: ignore[call-arg]
    assert "RATE_LIMIT_ENABLED" in str(exc_info.value)


def test_prod_with_rate_limit_enabled_ok(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "true")
    settings = Settings()  # type: ignore[call-arg]
    assert settings.rate_limit_enabled is True


def test_development_allows_rate_limit_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", _URL)
    monkeypatch.setenv("ENVIRONMENT", "development")
    monkeypatch.setenv("RATE_LIMIT_ENABLED", "false")
    settings = Settings()  # type: ignore[call-arg]
    assert settings.rate_limit_enabled is False
