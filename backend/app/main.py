"""FastAPI application entry point for the LPA backend."""

from __future__ import annotations

from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.middleware.cors import add_cors
from app.api.middleware.rate_limit import limiter, rate_limit_exceeded_handler
from app.api.routes import auth, members, organizations

app = FastAPI(title="LPA API", version="0.1.0")

app.state.limiter = limiter
# slowapi handler signature uses Exception but mypy expects ExceptionHandler[Exception]
app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)  # type: ignore[arg-type]

add_cors(app)
app.add_middleware(SlowAPIMiddleware)

app.include_router(auth.router)
app.include_router(members.router)
app.include_router(organizations.router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
