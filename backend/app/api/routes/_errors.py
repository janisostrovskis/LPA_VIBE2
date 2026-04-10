"""Shared helper: convert a use-case Result to an HTTP response or exception.

This module owns the mapping from DomainError subclasses to HTTP status codes
so each route need not duplicate the logic.
"""

from __future__ import annotations

from fastapi import HTTPException, status

from app.lib.errors import (
    ConflictError,
    DomainError,
    ForbiddenError,
    NotFoundError,
    UnauthorizedError,
    ValidationError,
)
from app.lib.result import Ok, Result

_ERROR_STATUS: dict[type[DomainError], int] = {
    ValidationError: 422,
    ConflictError: status.HTTP_409_CONFLICT,
    UnauthorizedError: status.HTTP_401_UNAUTHORIZED,
    ForbiddenError: status.HTTP_403_FORBIDDEN,
    NotFoundError: status.HTTP_404_NOT_FOUND,
}


def _domain_error_status(error: DomainError) -> int:
    """Return the HTTP status code for a domain error using MRO order."""
    for cls in type(error).__mro__:
        if cls in _ERROR_STATUS:
            return _ERROR_STATUS[cls]
    return status.HTTP_400_BAD_REQUEST


def result_to_response[T](result: Result[T, DomainError], success_status: int = 200) -> T:
    """Unwrap a Result, returning the Ok value or raising an HTTPException.

    The success_status argument is informational — the actual response code is
    set on the route decorator (FastAPI reads it from there). It is accepted here
    so callers remain self-documenting about their expected success code.
    """
    if isinstance(result, Ok):
        return result.value
    error = result.error
    http_status = _domain_error_status(error)
    raise HTTPException(status_code=http_status, detail=error.message)
