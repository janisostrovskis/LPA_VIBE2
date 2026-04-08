"""Tests for app.lib.logger — structured JSON logger."""

from __future__ import annotations

import json
import logging

import app.lib.logger as logger_module
import pytest
from app.lib.logger import _JsonFormatter, get_logger


def _reset() -> None:
    """Reset logger configuration between tests to allow level override testing."""
    logger_module._reset_for_testing()  # noqa: SLF001


def test_returns_logger_instance() -> None:
    _reset()
    assert isinstance(get_logger("test.x"), logging.Logger)


def test_same_name_returns_same_logger() -> None:
    _reset()
    a = get_logger("test.same")
    b = get_logger("test.same")
    assert a is b


def test_idempotent_single_handler() -> None:
    _reset()
    get_logger("test.idem1")
    get_logger("test.idem2")
    root = logging.getLogger()
    assert len(root.handlers) == 1


def test_json_output_keys(capsys: pytest.CaptureFixture[str]) -> None:
    _reset()
    log = get_logger("test.capsys.keys")
    log.info("hello world")
    captured = capsys.readouterr()
    parsed = json.loads(captured.out.strip())
    assert "ts" in parsed
    assert "level" in parsed
    assert "logger" in parsed
    assert "msg" in parsed
    assert parsed["msg"] == "hello world"
    assert parsed["level"] == "INFO"
    assert parsed["logger"] == "test.capsys.keys"


def test_json_warning_level(capsys: pytest.CaptureFixture[str]) -> None:
    _reset()
    log = get_logger("test.capsys.warn")
    log.warning("capsys message")
    captured = capsys.readouterr()
    parsed = json.loads(captured.out.strip())
    assert parsed["level"] == "WARNING"
    assert parsed["msg"] == "capsys message"
    assert parsed["ts"]


def test_json_formatter_directly() -> None:
    """Verify _JsonFormatter without relying on root logger state."""
    import io

    buf = io.StringIO()
    handler = logging.StreamHandler(buf)
    handler.setFormatter(_JsonFormatter())
    isolated = logging.getLogger("test.isolated.fmt")
    isolated.handlers = [handler]
    isolated.setLevel(logging.DEBUG)
    isolated.propagate = False
    isolated.info("structured message")
    parsed = json.loads(buf.getvalue().strip())
    assert parsed["msg"] == "structured message"
    assert parsed["logger"] == "test.isolated.fmt"


def test_env_log_level(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("LPA_LOG_LEVEL", "DEBUG")
    _reset()
    get_logger("test.level")
    assert logging.getLogger().level == logging.DEBUG
    # Restore: reset so subsequent tests re-configure at INFO
    _reset()
    monkeypatch.delenv("LPA_LOG_LEVEL", raising=False)
    get_logger("test.level.restore")
