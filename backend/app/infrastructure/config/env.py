"""Environment configuration loader.

Uses Pydantic Settings to parse env vars with fail-loudly validation.
Missing or malformed required variables cause Settings() instantiation
to raise pydantic.ValidationError with a clear per-field error.
"""
from enum import StrEnum
from functools import lru_cache

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class Settings(BaseSettings):  # type: ignore[explicit-any]
    """Application settings loaded from environment variables.

    Required: DATABASE_URL.
    Optional with defaults: BACKEND_PORT (8000), ENVIRONMENT (development),
    LPA_LOG_LEVEL (INFO), EMAIL_BACKEND (stub), AWS_DEFAULT_REGION (eu-north-1).
    Conditional: SES_FROM_EMAIL (required when EMAIL_BACKEND=ses).
    """

    database_url: str = Field(
        alias="DATABASE_URL",
        description="PostgreSQL connection string (psycopg3-compatible).",
        min_length=1,
    )
    backend_port: int = Field(
        default=8000,
        alias="BACKEND_PORT",
        ge=1,
        le=65535,
        description="Port the FastAPI app binds to.",
    )
    environment: Environment = Field(
        default=Environment.DEVELOPMENT,
        alias="ENVIRONMENT",
        description="Deployment environment name.",
    )
    log_level: LogLevel = Field(
        default=LogLevel.INFO,
        alias="LPA_LOG_LEVEL",
        description="Root logger level. Matches the env var app/lib/logger.py reads.",
    )

    email_backend: str = Field(
        default="stub",
        alias="EMAIL_BACKEND",
        pattern=r"^(stub|ses)$",
        description="Email sending backend: 'stub' (logs only) or 'ses' (Amazon SES).",
    )
    ses_from_email: str | None = Field(
        default=None,
        alias="SES_FROM_EMAIL",
        description="Verified SES sender email. Required when EMAIL_BACKEND=ses.",
    )
    aws_default_region: str = Field(
        default="eu-north-1",
        alias="AWS_DEFAULT_REGION",
        description="AWS region for SES. Defaults to eu-north-1 (Stockholm, closest to Latvia).",
    )

    redis_url: str = Field(
        default="redis://redis:6379/0",
        alias="REDIS_URL",
        description="Redis connection URL for general application use.",
    )
    celery_broker_url: str = Field(
        default="redis://redis:6379/0",
        alias="CELERY_BROKER_URL",
        description="Celery broker URL (Redis). Used by the email queue worker.",
    )
    rate_limit_redis_url: str = Field(
        default="redis://redis:6379/1",
        alias="RATE_LIMIT_REDIS_URL",
        description="Dedicated Redis DB for slowapi rate-limit counters.",
    )
    rate_limit_enabled: bool = Field(
        default=True,
        alias="RATE_LIMIT_ENABLED",
        description="Enable per-IP rate limiting on auth endpoints. Must be true in production.",
    )
    trusted_proxy_hops: int = Field(
        default=0,
        alias="TRUSTED_PROXY_HOPS",
        ge=0,
        description="Number of trusted reverse-proxy hops in front of the app. "
        "When > 0, the leftmost X-Forwarded-For entry is used as the client IP.",
    )

    @model_validator(mode="after")
    def _validate_ses_config(self) -> "Settings":
        if self.email_backend == "ses" and not self.ses_from_email:
            raise ValueError(
                "SES_FROM_EMAIL is required when EMAIL_BACKEND=ses"
            )
        return self

    @model_validator(mode="after")
    def _validate_rate_limit_in_prod(self) -> "Settings":
        if self.environment is Environment.PRODUCTION and not self.rate_limit_enabled:
            raise ValueError(
                "RATE_LIMIT_ENABLED must be true in production environment"
            )
        return self

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
        populate_by_name=True,
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return the cached Settings singleton.

    Call get_settings.cache_clear() in tests to force re-parsing after
    mutating the environment.
    """
    return Settings()  # type: ignore[call-arg]
