"""CORS middleware configuration for the LPA FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

_ALLOWED_ORIGINS = ["http://localhost:3000"]


def add_cors(app: FastAPI) -> None:
    """Add CORS middleware allowing the Next.js dev server origin."""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=_ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
