#!/usr/bin/env python3
"""
posttool_bash_scope_guard.py — PostToolUse hook that enforces scope.yaml
boundaries for files written via Bash (python heredoc, cat >, sed -i, etc.).

Contract:
  - Reads JSON from stdin (Claude Code PostToolUse hook schema).
  - Exits 0 if tool_name != "Bash".
  - Determines agent context from subagent_type field (absent = main session).
  - Reads pre-Bash baseline from .claude/bash-baseline.json.
    If baseline is missing or corrupt, fails open (exit 0).
  - Computes files that became dirty DURING the Bash call (post - baseline).
  - For each newly-dirty path outside the agent's allow list, reverts or removes
    the file and prints a BLOCKED message to stderr.
  - Exits 2 if any offenders were found, 0 otherwise.
  - On unexpected exception, logs to .claude/scope-hook-debug.log and exits 0
    (fail-open).

Revert strategy:
  - Tracked files (M, D, R in git status): `git checkout -- <path>`
  - Untracked new files (??): `rm -f <path>` (only if path is inside repo)

Trade-off note: we use git checkout for tracked reverts rather than a
pre-call file copy because (a) git already has the clean version and (b)
copying every file before each Bash call would be expensive. For untracked
files, git checkout is not applicable; we use rm -f instead. The risk is that
rm -f on an untracked file destroys work that was intentionally created outside
an agent's scope — accepted as the correct enforcement outcome.

Supports --selftest mode.
"""

import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
BASELINE_FILE: Path = REPO_ROOT / ".claude" / "bash-baseline.json"
DEBUG_LOG: Path = REPO_ROOT / ".claude" / "scope-hook-debug.log"

# Paths that are always allowed to change (tooling noise, generated caches).
IGNORE_PREFIXES = (
    "__pycache__/",
    ".pytest_cache/",
    ".ruff_cache/",
    ".mypy_cache/",
    "node_modules/",
    ".next/",
    "coverage/",
    "htmlcov/",
    ".claude/bash-baseline.json",
    ".claude/scope-hook-debug.log",
    ".claude/scope-override-audit.log",
)
IGNORE_SUFFIXES = (".pyc", ".pyo")


def _log_debug(message: str) -> None:
    """Append to debug log, fail-open."""
    try:
        with DEBUG_LOG.open("a", encoding="utf-8") as f:
            ts = datetime.now(tz=timezone.utc).isoformat()
            f.write(f"{ts}\tposttool_bash_scope_guard\t{message}\n")
    except Exception:  # noqa: BLE001
        pass  # FAIL-QUIET-EXCEPTION: debug log write must not block the session


def _import_scope_matcher():  # type: ignore[return]
    """
    Import scope_matcher from scripts/hooks/ co-located with this file.
    Uses importlib so hooks remain self-contained even when invoked from cwd
    that differs from repo root.
    """
    matcher_path = Path(__file__).resolve().parent / "scope_matcher.py"
    spec = importlib.util.spec_from_file_location("scope_matcher", matcher_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load scope_matcher from {matcher_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _parse_porcelain(porcelain: str) -> set[str]:
    """
    Parse `git status --porcelain=v1` output into a set of forward-slash
    relative file paths.  Handles XY-flag lines and rename lines (R old -> new).
    """
    paths: set[str] = set()
    for line in porcelain.splitlines():
        if len(line) < 4:
            continue
        # Columns 0-1 are XY flags, column 2 is space, rest is filename(s).
        rest = line[3:]
        # Rename lines look like "old -> new" or "old\0new" in porcelain v1;
        # v1 uses " -> " separator for renames.
        if " -> " in rest:
            _, _, new = rest.partition(" -> ")
            paths.add(new.strip().replace("\\", "/"))
        else:
            paths.add(rest.strip().replace("\\", "/"))
    return paths


def _should_ignore(rel_path: str) -> bool:
    """Return True if rel_path matches any ignore rule."""
    p = rel_path.replace("\\", "/")
    if any(p.startswith(prefix) for prefix in IGNORE_PREFIXES):
        return True
    if p == ".claude/bash-baseline.json":
        return True
    if any(p.endswith(suffix) for suffix in IGNORE_SUFFIXES):
        return True
    # Ignore any path containing __pycache__/ as a segment
    if "__pycache__/" in p:
        return True
    return False


def _git_status_porcelain(repo_root: Path) -> str:
    """Run git status --porcelain=v1 and return stdout."""
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(repo_root),
    )
    return result.stdout


def _revert_file(rel_path: str, is_untracked: bool, repo_root: Path) -> str:
    """
    Revert a file to its pre-Bash state.
    Returns a short description of the action taken.
    """
    abs_path = repo_root / Path(rel_path)
    if is_untracked:
        # New file not in git — remove it (only if safely inside repo)
        try:
            abs_path.relative_to(repo_root)  # safety check
            if abs_path.exists():
                abs_path.unlink()
            return "removed"
        except ValueError:
            return "NOT-REMOVED (outside repo)"
    else:
        # Tracked file — use git to restore
        result = subprocess.run(
            ["git", "checkout", "--", rel_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=str(repo_root),
        )
        if result.returncode == 0:
            return "reverted"
        return f"revert-failed: {result.stderr.strip()}"


def run_guard(stdin_data: str, repo_root: Path = REPO_ROOT) -> int:
    """Core guard logic. Returns 0 (allow) or 2 (blocked)."""
    try:
        payload = json.loads(stdin_data)
    except (json.JSONDecodeError, ValueError) as exc:
        _log_debug(f"JSON parse error: {exc}")
        return 0

    if not isinstance(payload, dict):
        return 0

    tool_name = payload.get("tool_name", "")
    if tool_name != "Bash":
        return 0

    # Determine agent context
    agent_raw = payload.get("subagent_type") or ""
    agent = str(agent_raw).strip() or "main_session"

    # Load baseline
    baseline_file = repo_root / ".claude" / "bash-baseline.json"
    try:
        baseline_data = json.loads(baseline_file.read_text(encoding="utf-8"))
        baseline_porcelain = baseline_data.get("porcelain", "")
    except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError) as exc:
        _log_debug(f"baseline load error (fail-open): {exc}")
        return 0  # fail-open

    baseline_dirty = _parse_porcelain(baseline_porcelain)
    post_porcelain = _git_status_porcelain(repo_root)
    post_dirty = _parse_porcelain(post_porcelain)

    changed_during_bash = post_dirty - baseline_dirty

    if not changed_during_bash:
        return 0

    # Load scope manifest
    try:
        sm = _import_scope_matcher()
        manifest = sm.load_manifest(repo_root)
    except Exception as exc:  # noqa: BLE001
        _log_debug(f"scope_matcher load error (fail-open): {exc}")
        return 0

    # Check each newly-dirty path
    offenders: list[tuple[str, str, str]] = []  # (rel_path, owner_agent, action)

    for rel_path in sorted(changed_during_bash):
        if _should_ignore(rel_path):
            continue

        try:
            allowed = sm.agent_allows(manifest, agent, rel_path)
        except KeyError:
            # Unknown agent — treat as main_session
            try:
                allowed = sm.agent_allows(manifest, "main_session", rel_path)
            except Exception:  # noqa: BLE001
                allowed = True  # fail-open for unknown agents

        if allowed:
            continue

        # Find owner for message
        agents_map = (manifest.get("agents") or {})
        owner: str | None = None
        for a_name in agents_map:
            try:
                if sm.agent_allows(manifest, a_name, rel_path):
                    owner = a_name
                    break
            except Exception:  # noqa: BLE001
                pass

        # Determine if untracked
        # Lines starting with "??" in post_porcelain are untracked
        is_untracked = any(
            line[3:].strip().replace("\\", "/") == rel_path
            and line[:2] == "??"
            for line in post_porcelain.splitlines()
            if len(line) >= 4
        )

        action = _revert_file(rel_path, is_untracked, repo_root)
        owner_str = owner or "no agent"
        offenders.append((rel_path, owner_str, action))

    if not offenders:
        return 0

    # Print BLOCKED message
    print("BLOCKED: Bash wrote files outside agent scope. Changes reverted.", file=sys.stderr)
    print(f"  Agent: {agent}", file=sys.stderr)
    for rel_path, owner_str, action in offenders:
        print(
            f"  {rel_path}  [owner: {owner_str}]  [{action}]",
            file=sys.stderr,
        )
    print(
        "Delegate file-writing to the owning agent or request a scope amendment.",
        file=sys.stderr,
    )
    return 2


def run_selftest() -> int:
    """
    5 selftest cases using a tempdir with a fake git repo.
    Returns 0 if all pass, 1 if any fail.

    Trade-off: we use `git init` + commits inside the tempdir so that
    `git checkout --` can restore baseline-tracked files.  For untracked-file
    removal we rely on the rm-f path.  The alternative (storing file copies)
    would avoid needing git but would not exercise the actual revert code path.
    We accept the slightly heavier setup for better fidelity.
    """
    import tempfile

    failures: list[str] = []

    # Save real REPO_ROOT to restore after patching
    original_root = globals()["REPO_ROOT"]

    with tempfile.TemporaryDirectory() as tmpdir:
        root = Path(tmpdir)
        dot_claude = root / ".claude"
        dot_claude.mkdir()

        git_env = {
            **os.environ,
            "GIT_AUTHOR_NAME": "test",
            "GIT_AUTHOR_EMAIL": "test@test",
            "GIT_COMMITTER_NAME": "test",
            "GIT_COMMITTER_EMAIL": "test@test",
        }

        # Initialise git repo
        subprocess.run(["git", "init", str(root)], capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@test"],
            capture_output=True, cwd=str(root),
        )
        subprocess.run(
            ["git", "config", "user.name", "test"],
            capture_output=True, cwd=str(root),
        )

        # Build a minimal scope.yaml inside tmpdir
        scope_content = """
main_session:
  allow:
    - "CLAUDE.md"
    - ".claude/**"
    - "planning/**"
    - "docs/**"
agents:
  devops-agent:
    allow:
      - "scripts/**"
      - ".github/**"
      - "docker-compose.yml"
      - "CLAUDE.md"
"""
        (dot_claude / "scope.yaml").write_text(scope_content, encoding="utf-8")

        def write_baseline(repo_root: Path) -> None:
            porcelain = _git_status_porcelain(repo_root)
            baseline = {"ts": datetime.now(tz=timezone.utc).isoformat(), "porcelain": porcelain}
            (repo_root / ".claude" / "bash-baseline.json").write_text(
                json.dumps(baseline), encoding="utf-8"
            )

        def make_payload(agent: str = "") -> str:
            p: dict = {"tool_name": "Bash", "tool_input": {"command": "echo test"}}
            if agent:
                p["subagent_type"] = agent
            return json.dumps(p)

        # Patch REPO_ROOT to point at our tempdir
        globals()["REPO_ROOT"] = root
        try:
            # -------------------------------------------------------------------
            # (a) Main-session Bash touches planning/foo.md (in main scope) → exit 0
            # -------------------------------------------------------------------
            planning_dir = root / "planning"
            planning_dir.mkdir()
            write_baseline(root)
            (planning_dir / "foo.md").write_text("hello", encoding="utf-8")
            code = run_guard(make_payload(), repo_root=root)
            if code != 0:
                failures.append(f"(a) expected exit 0, got {code}")
            # File should still exist
            if not (planning_dir / "foo.md").exists():
                failures.append("(a) planning/foo.md was incorrectly removed")
            # Clean up for next case
            (planning_dir / "foo.md").unlink(missing_ok=True)

            # -------------------------------------------------------------------
            # (b) Main-session Bash touches backend/app/domain/entities/user.py
            #     (out of main scope) → exit 2, file reverted
            # -------------------------------------------------------------------
            # Commit a baseline version of user.py so git checkout works
            entity_dir = root / "backend" / "app" / "domain" / "entities"
            entity_dir.mkdir(parents=True)
            user_py = entity_dir / "user.py"
            user_py.write_text("# baseline\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=str(root), capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "baseline"],
                cwd=str(root), capture_output=True, env=git_env,
            )
            write_baseline(root)
            # Simulate Bash writing to user.py
            user_py.write_text("# rogue edit\n", encoding="utf-8")
            code = run_guard(make_payload(), repo_root=root)
            if code != 2:
                failures.append(f"(b) expected exit 2, got {code}")
            # File should be reverted to baseline content
            if user_py.read_text() != "# baseline\n":
                failures.append(
                    f"(b) user.py not reverted; content: {user_py.read_text()!r}"
                )

            # -------------------------------------------------------------------
            # (c) devops-agent Bash touches scripts/foo.py (in devops scope) → exit 0
            # -------------------------------------------------------------------
            scripts_dir = root / "scripts"
            scripts_dir.mkdir(exist_ok=True)
            write_baseline(root)
            (scripts_dir / "foo.py").write_text("# ok\n", encoding="utf-8")
            code = run_guard(make_payload("devops-agent"), repo_root=root)
            if code != 0:
                failures.append(f"(c) expected exit 0, got {code}")
            if not (scripts_dir / "foo.py").exists():
                failures.append("(c) scripts/foo.py was incorrectly removed")
            (scripts_dir / "foo.py").unlink(missing_ok=True)

            # -------------------------------------------------------------------
            # (d) devops-agent Bash touches CLAUDE.md — CLAUDE.md is in devops
            #     allow list for this test scope, so expect exit 0.
            #     (Real repo has CLAUDE.md in efficiency-agent scope, but here
            #      we test the scope enforcement logic, not the real manifest.)
            #     Adjust: test with a file NOT in devops scope — backend/app/x.py
            # -------------------------------------------------------------------
            backend_app = root / "backend" / "app"
            backend_app.mkdir(parents=True, exist_ok=True)
            # Commit x.py as tracked baseline
            x_py = backend_app / "x.py"
            x_py.write_text("# baseline\n", encoding="utf-8")
            subprocess.run(["git", "add", "-A"], cwd=str(root), capture_output=True)
            subprocess.run(
                ["git", "commit", "-m", "baseline2"],
                cwd=str(root), capture_output=True, env=git_env,
            )
            write_baseline(root)
            x_py.write_text("# rogue\n", encoding="utf-8")
            code = run_guard(make_payload("devops-agent"), repo_root=root)
            if code != 2:
                failures.append(f"(d) expected exit 2 for devops touching backend/app/x.py, got {code}")
            if x_py.read_text() != "# baseline\n":
                failures.append(f"(d) backend/app/x.py not reverted; content: {x_py.read_text()!r}")

            # -------------------------------------------------------------------
            # (e) Bash creates untracked frontend/src/rogue.tsx
            #     main session — out of scope → exit 2, file deleted
            # -------------------------------------------------------------------
            frontend_src = root / "frontend" / "src"
            frontend_src.mkdir(parents=True, exist_ok=True)
            write_baseline(root)
            rogue = frontend_src / "rogue.tsx"
            rogue.write_text("// rogue\n", encoding="utf-8")
            code = run_guard(make_payload(), repo_root=root)
            if code != 2:
                failures.append(f"(e) expected exit 2, got {code}")
            if rogue.exists():
                failures.append("(e) frontend/src/rogue.tsx was NOT deleted")

        finally:
            globals()["REPO_ROOT"] = original_root

    if failures:
        print("posttool_bash_scope_guard.py selftest FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1

    print("posttool_bash_scope_guard.py selftest: all 5 assertions passed.")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return run_selftest()

    stdin_data = sys.stdin.read()
    try:
        return run_guard(stdin_data)
    except Exception as exc:  # noqa: BLE001
        _log_debug(f"unhandled exception in run_guard: {exc}")
        return 0  # fail-open


if __name__ == "__main__":
    sys.exit(main())
