"""Per-IP rate limiting via slowapi, Redis-backed, fail-open on broker outage."""
from __future__ import annotations

from typing import cast

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi import Limiter
from slowapi.errors import RateLimitExceeded

from app.infrastructure.config.env import get_settings

_settings = get_settings()


def _ip_key_func(request: Request) -> str:
    """Extract client IP honoring TRUSTED_PROXY_HOPS.

    Convention: reverse proxies append to X-Forwarded-For on the right, so
    with N trusted hops the client IP is ``parts[-hops]``. Using ``parts[0]``
    would be spoofable — an attacker can send ``X-Forwarded-For: attacker``
    and the outermost proxy appends its own entry, leaving ``parts[0]``
    attacker-controlled. When ``hops == 0`` we ignore XFF entirely and use
    ``request.client.host`` which FastAPI/Starlette does not let userland spoof.
    """
    hops = _settings.trusted_proxy_hops
    if hops > 0:
        xff = request.headers.get("X-Forwarded-For", "")
        if xff:
            parts = [p.strip() for p in xff.split(",") if p.strip()]
            if len(parts) >= hops:
                return parts[-hops]
    if request.client is not None:
        return request.client.host or "unknown"
    return "unknown"


limiter = Limiter(
    key_func=_ip_key_func,
    storage_uri=_settings.rate_limit_redis_url,
    enabled=_settings.rate_limit_enabled,
    swallow_errors=True,  # fail-open on Redis outage
)


def rate_limit_exceeded_handler(
    request: Request, exc: Exception
) -> JSONResponse:
    """Convert slowapi RateLimitExceeded into the project error envelope."""
    rle = cast(RateLimitExceeded, exc)
    retry_after = str(int(getattr(rle, "retry_after", 60)))
    return JSONResponse(
        status_code=429,
        content={
            "detail": {
                "code": "rate_limited",
                "message": "Too many requests. Try again later.",
            }
        },
        headers={"Retry-After": retry_after},
    )
