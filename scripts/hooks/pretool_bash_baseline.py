#!/usr/bin/env python3
"""
pretool_bash_baseline.py — PreToolUse hook that snapshots the git working-tree
state before a Bash call so the PostToolUse guard can diff against it.

Contract:
  - Reads JSON from stdin (Claude Code PreToolUse hook schema).
  - If tool_name != "Bash", exits 0 immediately (defensive).
  - Runs `git status --porcelain=v1 --untracked-files=all` and writes the raw
    output to .claude/bash-baseline.json as:
      {"ts": "<iso>", "porcelain": "<raw text>"}
  - Always exits 0 — this hook is purely informational.  Fail-open on any error.
  - On exception, logs to .claude/scope-hook-debug.log and exits 0.

Supports --selftest mode.
"""

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
BASELINE_FILE: Path = REPO_ROOT / ".claude" / "bash-baseline.json"
DEBUG_LOG: Path = REPO_ROOT / ".claude" / "scope-hook-debug.log"


def _log_debug(message: str) -> None:
    """Append to debug log, fail-open."""
    try:
        with DEBUG_LOG.open("a", encoding="utf-8") as f:
            ts = datetime.now(tz=timezone.utc).isoformat()
            f.write(f"{ts}\tpretool_bash_baseline\t{message}\n")
    except Exception:  # noqa: BLE001
        pass  # FAIL-QUIET-EXCEPTION: debug log write must not block the session


def _snapshot_baseline(repo_root: Path = REPO_ROOT) -> None:
    """Run git status and write baseline file."""
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True,
        text=True,
        cwd=str(repo_root),
    )
    baseline = {
        "ts": datetime.now(tz=timezone.utc).isoformat(),
        "porcelain": result.stdout,
    }
    baseline_file = repo_root / ".claude" / "bash-baseline.json"
    baseline_file.parent.mkdir(parents=True, exist_ok=True)
    baseline_file.write_text(json.dumps(baseline), encoding="utf-8")


def run_hook(stdin_data: str, repo_root: Path = REPO_ROOT) -> int:
    """Core hook logic. Returns 0 always (fail-open)."""
    try:
        payload = json.loads(stdin_data)
    except (json.JSONDecodeError, ValueError) as exc:
        _log_debug(f"JSON parse error: {exc}")
        return 0

    if not isinstance(payload, dict):
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name != "Bash":
        return 0  # defensive — matcher should already filter

    try:
        _snapshot_baseline(repo_root)
    except Exception as exc:  # noqa: BLE001
        _log_debug(f"snapshot error: {exc}")

    return 0


def run_selftest() -> int:
    """
    2 selftest cases using a tempdir with a fake git repo.
    Returns 0 if all pass, 1 if any fail.
    """
    import tempfile

    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        dot_claude = root / ".claude"
        dot_claude.mkdir()

        # Initialise a minimal git repo so git status works
        subprocess.run(["git", "init", str(root)], capture_output=True)
        subprocess.run(
            ["git", "commit", "--allow-empty", "-m", "init"],
            capture_output=True,
            cwd=str(root),
            env={**__import__("os").environ, "GIT_AUTHOR_NAME": "t",
                 "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t",
                 "GIT_COMMITTER_EMAIL": "t@t"},
        )

        baseline_file = dot_claude / "bash-baseline.json"

        # (a) Bash payload: baseline file should be written
        bash_payload = json.dumps({"tool_name": "Bash", "tool_input": {"command": "ls"}})
        code = run_hook(bash_payload, repo_root=root)
        if code != 0:
            failures.append(f"(a) expected exit 0, got {code}")
        if not baseline_file.exists():
            failures.append("(a) baseline file was not created")
        else:
            try:
                data = json.loads(baseline_file.read_text())
                if "ts" not in data or "porcelain" not in data:
                    failures.append("(a) baseline JSON missing ts or porcelain keys")
            except (json.JSONDecodeError, ValueError) as exc:
                failures.append(f"(a) baseline JSON parse error: {exc}")
            # Remove for next case
            baseline_file.unlink()

        # (b) Non-Bash payload: baseline file should NOT be created
        read_payload = json.dumps({"tool_name": "Read", "tool_input": {"file_path": "/tmp/foo"}})
        code = run_hook(read_payload, repo_root=root)
        if code != 0:
            failures.append(f"(b) expected exit 0, got {code}")
        if baseline_file.exists():
            failures.append("(b) baseline file was created for non-Bash tool (unexpected)")

    if failures:
        print("pretool_bash_baseline.py selftest FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1

    print("pretool_bash_baseline.py selftest: all 2 assertions passed.")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return run_selftest()

    stdin_data = sys.stdin.read()
    return run_hook(stdin_data)


if __name__ == "__main__":
    sys.exit(main())
