"""FastAPI application entry point for the LPA backend."""

from __future__ import annotations

from fastapi import FastAPI

from app.api.middleware.cors import add_cors
from app.api.routes import auth, members, organizations

app = FastAPI(title="LPA API", version="0.1.0")

add_cors(app)

app.include_router(auth.router)
app.include_router(members.router)
app.include_router(organizations.router)


@app.get("/health", tags=["system"])
async def health() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
