#!/usr/bin/env python3
"""
pretool_scope_guard.py — PreToolUse hook that enforces .claude/scope.yaml boundaries.

Contract:
  - Reads JSON from stdin (Claude Code PreToolUse hook schema).
  - If tool_name is not Write or Edit, exits 0 immediately.
  - Determines agent context from hook input (agent_type / subagent_type fields).
  - Checks the file_path against the applicable allow list from scope.yaml.
  - Blocks (exit 2) on path mismatch with a descriptive message to stderr.
  - Allows (exit 0) with override if .claude/scope-override exists and is non-empty.
  - Logs all parse errors to .claude/scope-hook-debug.log and exits 0 (fail-open).

Exit codes:
  0 — allowed (or irrelevant tool, or fail-open on error)
  2 — blocked

Supports --selftest mode to verify the hook's own correctness.
"""

import fnmatch
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

# Repo root is two directories above this file: repo/scripts/hooks/pretool_scope_guard.py
REPO_ROOT: Path = Path(__file__).resolve().parents[2]

SCOPE_YAML_PATH: Path = REPO_ROOT / ".claude" / "scope.yaml"
OVERRIDE_FILE: Path = REPO_ROOT / ".claude" / "scope-override"
AUDIT_LOG: Path = REPO_ROOT / ".claude" / "scope-override-audit.log"
DEBUG_LOG: Path = REPO_ROOT / ".claude" / "scope-hook-debug.log"

GUARDED_TOOLS = {"Write", "Edit"}


# ---------------------------------------------------------------------------
# Minimal YAML parser — handles only the subset used by scope.yaml:
#   maps, lists, strings, comments, indented blocks.
# We prefer PyYAML when available; this is the fallback.
# ---------------------------------------------------------------------------

def _parse_yaml_minimal(text: str) -> dict:
    """
    Tiny YAML subset parser for scope.yaml.
    Supports: mapping keys, string values, lists with '- ' items, comments (#),
    and multi-level indentation.  Does not support anchors, tags, or multi-line
    scalars.
    """
    lines = text.splitlines()
    # Remove blank lines and comment-only lines, but keep track of indentation.
    tokens: list[tuple[int, str]] = []
    for line in lines:
        stripped = line.rstrip()
        if not stripped or stripped.lstrip().startswith("#"):
            continue
        indent = len(stripped) - len(stripped.lstrip())
        content = stripped.lstrip()
        # Strip inline comments
        if " #" in content:
            content = content[: content.index(" #")].rstrip()
        tokens.append((indent, content))

    def parse_value(v: str) -> str:
        """Strip optional quotes from a scalar value."""
        v = v.strip()
        if (v.startswith('"') and v.endswith('"')) or (
            v.startswith("'") and v.endswith("'")
        ):
            return v[1:-1]
        return v

    def parse_block(start: int, base_indent: int) -> tuple[object, int]:
        """
        Parse a block starting at tokens[start] with indent > base_indent.
        Returns (value, next_index).
        """
        i = start
        # Determine the indent level of this block
        if i >= len(tokens):
            return {}, i
        block_indent = tokens[i][0]

        # Detect if this is a list block
        if tokens[i][1].startswith("- "):
            items: list[str] = []
            while i < len(tokens) and tokens[i][0] == block_indent:
                line = tokens[i][1]
                if line.startswith("- "):
                    items.append(parse_value(line[2:]))
                    i += 1
                else:
                    break
            return items, i

        # Otherwise it's a mapping
        mapping: dict = {}
        while i < len(tokens) and tokens[i][0] >= block_indent:
            indent, line = tokens[i]
            if indent != block_indent:
                # Belongs to a nested block — should have been consumed already.
                break
            if ":" in line:
                key, _, rest = line.partition(":")
                key = key.strip()
                rest = rest.strip()
                if rest:
                    # Inline value
                    mapping[key] = parse_value(rest)
                    i += 1
                else:
                    # Block value on next line(s)
                    i += 1
                    if i < len(tokens) and tokens[i][0] > block_indent:
                        value, i = parse_block(i, block_indent)
                        mapping[key] = value
                    else:
                        mapping[key] = {}
            else:
                # Not a key: value line — skip
                i += 1
        return mapping, i

    if not tokens:
        return {}
    result, _ = parse_block(0, -1)
    return result if isinstance(result, dict) else {}


def load_scope_yaml(path: Path) -> dict:
    """Load and parse scope.yaml, preferring PyYAML."""
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore[import-untyped]
        return yaml.safe_load(text) or {}
    except ImportError:
        return _parse_yaml_minimal(text)


def log_debug(message: str) -> None:
    """Append a debug message to the debug log file (fail-open)."""
    try:
        with DEBUG_LOG.open("a", encoding="utf-8") as f:
            ts = datetime.now(tz=timezone.utc).isoformat()
            f.write(f"{ts}\t{message}\n")
    except Exception:  # noqa: BLE001
        pass  # FAIL-QUIET-EXCEPTION: debug log write failure must not block the session


def path_matches_any(rel_path: str, globs: list[str]) -> bool:
    """Return True if rel_path matches any of the given glob patterns."""
    # Normalise to forward slashes for consistent fnmatch behaviour.
    rel_posix = PurePosixPath(rel_path.replace("\\", "/")).as_posix()
    for pattern in globs:
        pattern_posix = pattern.replace("\\", "/")
        if fnmatch.fnmatch(rel_posix, pattern_posix):
            return True
        # Also try matching the path against the pattern without the leading segment
        # to handle both "frontend/src/app/page.tsx" and patterns like "frontend/src/**"
        if fnmatch.fnmatch(rel_posix, pattern_posix):
            return True
    return False


def find_owning_agent(rel_path: str, agents: dict) -> str | None:
    """Return the name of the first agent whose allow list matches rel_path."""
    for agent_name, agent_data in agents.items():
        if not isinstance(agent_data, dict):
            continue
        allow_list = agent_data.get("allow", [])
        if isinstance(allow_list, list) and path_matches_any(rel_path, allow_list):
            return agent_name
    return None


def consume_override(rel_path: str) -> bool:
    """
    If .claude/scope-override exists and is non-empty, consume it:
    log to audit file, delete override, return True.
    Otherwise return False.
    """
    if not OVERRIDE_FILE.exists():
        return False
    reason = OVERRIDE_FILE.read_text(encoding="utf-8").strip()
    if not reason:
        return False
    # Append to audit log
    ts = datetime.now(tz=timezone.utc).isoformat()
    try:
        with AUDIT_LOG.open("a", encoding="utf-8") as f:
            f.write(f"{ts}\t{rel_path}\t{reason}\n")
    except Exception:  # noqa: BLE001
        pass  # FAIL-QUIET-EXCEPTION: audit log write failure; override still consumed
    # Delete the override file (single-shot)
    try:
        OVERRIDE_FILE.unlink()
    except Exception:  # noqa: BLE001
        pass  # FAIL-QUIET-EXCEPTION: unlink failure; treated as consumed
    return True


def run_guard(stdin_data: str, repo_root: Path = REPO_ROOT) -> int:
    """
    Core guard logic.  Returns intended exit code (0 = allow, 2 = block).
    Exposed as a function for testability.
    """
    try:
        payload = json.loads(stdin_data)
    except (json.JSONDecodeError, ValueError) as exc:
        log_debug(f"JSON parse error: {exc}")
        return 0  # fail-open

    if not isinstance(payload, dict):
        log_debug("Payload is not a dict")
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name not in GUARDED_TOOLS:
        return 0

    tool_input = payload.get("tool_input", {})
    if not isinstance(tool_input, dict):
        log_debug("tool_input is not a dict")
        return 0

    file_path_raw = tool_input.get("file_path", "")
    if not file_path_raw:
        return 0

    # Compute path relative to repo root
    try:
        abs_path = Path(file_path_raw).resolve()
        rel_path = str(abs_path.relative_to(repo_root))
    except ValueError:
        # Path is outside repo root — not our concern
        return 0
    except Exception as exc:
        log_debug(f"Path resolution error for {file_path_raw!r}: {exc}")
        return 0

    # Normalise separators
    rel_path = rel_path.replace("\\", "/")

    # Load scope manifest
    scope_yaml_path = repo_root / ".claude" / "scope.yaml"
    try:
        scope = load_scope_yaml(scope_yaml_path)
    except Exception as exc:
        log_debug(f"scope.yaml load error: {exc}")
        return 0  # fail-open

    if not isinstance(scope, dict):
        log_debug("scope.yaml did not parse to a dict")
        return 0

    # Determine agent context
    # Claude Code may supply agent_type or subagent_type; absent = main session.
    agent_type = (
        payload.get("agent_type")
        or payload.get("subagent_type")
        or ""
    )
    agent_type = str(agent_type).strip()

    agents = scope.get("agents", {}) or {}

    if agent_type and agent_type in agents:
        # Subagent path — check against that agent's allow list
        agent_data = agents[agent_type]
        allow_list = agent_data.get("allow", []) if isinstance(agent_data, dict) else []
        if not isinstance(allow_list, list):
            allow_list = []
        if path_matches_any(rel_path, allow_list):
            return 0
        # Find which agent actually owns this path (for a helpful message)
        owner = find_owning_agent(rel_path, agents)
        owner_msg = f"owned by {owner}" if owner else "not in any agent's allow list"
        print(
            f"BLOCKED: {agent_type} cannot edit {rel_path}.\n"
            f"That path is {owner_msg} (per .claude/scope.yaml).\n"
            f"Delegate to the correct agent or request a scope amendment.",
            file=sys.stderr,
        )
        return 2

    # Main session path — check against main_session.allow
    main_cfg = scope.get("main_session", {}) or {}
    main_allow = main_cfg.get("allow", []) if isinstance(main_cfg, dict) else []
    if not isinstance(main_allow, list):
        main_allow = []

    if path_matches_any(rel_path, main_allow):
        return 0

    # Check for override
    override_file = repo_root / ".claude" / "scope-override"
    override_audit = repo_root / ".claude" / "scope-override-audit.log"
    if override_file.exists():
        reason = override_file.read_text(encoding="utf-8").strip()
        if reason:
            ts = datetime.now(tz=timezone.utc).isoformat()
            try:
                with override_audit.open("a", encoding="utf-8") as f:
                    f.write(f"{ts}\t{rel_path}\t{reason}\n")
            except Exception:  # noqa: BLE001
                pass
            try:
                override_file.unlink()
            except Exception:  # noqa: BLE001
                pass
            return 0

    # Blocked — find owning agent for helpful message
    owner = find_owning_agent(rel_path, agents)
    if owner:
        delegate_hint = f'Delegate via Agent(subagent_type="{owner}", ...).'
    else:
        delegate_hint = "No agent currently owns this path; check .claude/scope.yaml."

    print(
        f"BLOCKED: Main session cannot edit {rel_path}.\n"
        f"This file belongs to {owner or 'an unregistered scope'} "
        f"(per .claude/scope.yaml).\n"
        f"{delegate_hint}\n"
        f"Emergency override: "
        f'`touch .claude/scope-override && echo "<reason>" > .claude/scope-override`,'
        f" then retry. Override is consumed on next edit.",
        file=sys.stderr,
    )
    return 2


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def run_selftest() -> int:
    """
    Run 4 self-test assertions.  Returns 0 if all pass, 1 if any fail.
    """
    import shutil

    failures: list[str] = []

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)

        # Build a minimal .claude/scope.yaml inside tmpdir
        dot_claude = root / ".claude"
        dot_claude.mkdir()

        scope_content = """
main_session:
  allow:
    - "CLAUDE.md"
    - ".claude/**"
    - "planning/**"
    - "docs/**"
agents:
  frontend-agent:
    allow:
      - "frontend/src/**"
  devops-agent:
    allow:
      - "scripts/**"
      - ".claude/settings.json"
"""
        (dot_claude / "scope.yaml").write_text(scope_content, encoding="utf-8")

        def make_payload(
            tool: str,
            file_path: str,
            agent_type: str = "",
        ) -> str:
            p: dict = {"tool_name": tool, "tool_input": {"file_path": str(root / file_path.replace("/", os.sep))}}
            if agent_type:
                p["agent_type"] = agent_type
            return json.dumps(p)

        # Monkey-patch REPO_ROOT for this test
        original_root = globals()["REPO_ROOT"]
        globals()["REPO_ROOT"] = root
        try:
            # (a) Main session edit to frontend/src/app/page.tsx → expect 2
            code = run_guard(make_payload("Edit", "frontend/src/app/page.tsx"), repo_root=root)
            if code != 2:
                failures.append(f"(a) expected exit 2, got {code}")

            # (b) Main session edit to CLAUDE.md → expect 0
            code = run_guard(make_payload("Edit", "CLAUDE.md"), repo_root=root)
            if code != 0:
                failures.append(f"(b) expected exit 0, got {code}")

            # (c) Override file consumed on use
            override_path = dot_claude / "scope-override"
            override_path.write_text("test override reason", encoding="utf-8")
            code = run_guard(make_payload("Edit", "frontend/src/app/page.tsx"), repo_root=root)
            if code != 0:
                failures.append(f"(c) override: expected exit 0, got {code}")
            if override_path.exists():
                failures.append("(c) override file was NOT consumed (still exists)")
            audit_log = dot_claude / "scope-override-audit.log"
            if not audit_log.exists():
                failures.append("(c) audit log was not created")

            # (d) Unknown tool_name → expect 0
            code = run_guard(
                json.dumps({"tool_name": "Read", "tool_input": {"file_path": str(root / "frontend/src/app/page.tsx")}}),
                repo_root=root,
            )
            if code != 0:
                failures.append(f"(d) expected exit 0 for Read tool, got {code}")

        finally:
            globals()["REPO_ROOT"] = original_root

    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("pretool_scope_guard.py selftest: all 4 assertions passed.")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return run_selftest()

    stdin_data = sys.stdin.read()
    return run_guard(stdin_data)


if __name__ == "__main__":
    sys.exit(main())
