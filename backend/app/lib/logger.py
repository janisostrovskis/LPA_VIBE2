"""Structured logger. Stdlib only.

Reads LPA_LOG_LEVEL directly from os.environ. This is the one place lib/
is allowed to read env vars — env.py (00f) will use get_logger itself, so
the reverse dependency must not exist.
"""

import json
import logging
import os
import sys
from datetime import UTC, datetime

_CONFIGURED = False

_RESERVED_LOG_ATTRS = frozenset({
    "name", "msg", "args", "levelname", "levelno", "pathname", "filename",
    "module", "exc_info", "exc_text", "stack_info", "lineno", "funcName",
    "created", "msecs", "relativeCreated", "thread", "threadName",
    "processName", "process", "message", "taskName",
})


class _JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, object] = {
            "ts": datetime.fromtimestamp(record.created, tz=UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "msg": record.getMessage(),
        }
        extras = {k: v for k, v in record.__dict__.items() if k not in _RESERVED_LOG_ATTRS}
        if extras:
            payload["extra"] = extras
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


def _configure() -> None:
    global _CONFIGURED  # noqa: PLW0603 — intentional module-level guard
    if _CONFIGURED:
        return
    level_name = os.environ.get("LPA_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_JsonFormatter())
    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(level)
    _CONFIGURED = True


def _reset_for_testing() -> None:
    """Reset configuration state. Only for use in tests."""
    global _CONFIGURED  # noqa: PLW0603
    _CONFIGURED = False


def get_logger(name: str) -> logging.Logger:
    _configure()
    return logging.getLogger(name)
