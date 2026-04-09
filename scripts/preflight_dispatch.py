#!/usr/bin/env python3
"""
preflight_dispatch.py — Pre-flight scope check for orchestrator dispatch.

Validates that every file a brief plans to touch is within the target agent's
.claude/scope.yaml allow list.  Run this before Agent(...) to catch out-of-scope
dispatches before they cost a roundtrip.

Usage:
    python scripts/preflight_dispatch.py \\
        --agent <agent-name> \\
        --files <file1> <file2> ... \\
        [--strict | --loose]

Exit codes:
    0 — every file is in scope (dispatchable)
    1 — at least one scope violation OR (in --strict) a non-existent file
    2 — config error (scope.yaml missing/malformed, unknown agent, no --files)

Supports --selftest.
"""

import argparse
import re
import sys
import tempfile
from pathlib import Path

# Repo root: this script lives at repo/scripts/preflight_dispatch.py
_REPO_ROOT = Path(__file__).resolve().parent.parent

# Patterns that indicate "source files" — triggers a REMINDER line.
_SOURCE_PATTERNS = [
    re.compile(r"^backend/app/"),
    re.compile(r"^frontend/src/"),
]


def _is_source_file(rel_path: str) -> bool:
    for pat in _SOURCE_PATTERNS:
        if pat.match(rel_path):
            return True
    return False


def _import_scope_matcher():  # type: ignore[return]
    """
    Import scope_matcher from the hooks directory co-located with this script.
    scope_matcher is part of the tooling, so it always loads relative to this
    file's location — not relative to the project root under test.
    """
    import importlib.util

    # This script lives at repo/scripts/; scope_matcher is at repo/scripts/hooks/
    matcher_path = Path(__file__).resolve().parent / "hooks" / "scope_matcher.py"
    spec = importlib.util.spec_from_file_location("scope_matcher", matcher_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load scope_matcher from {matcher_path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _normalize_rel(file_arg: str, repo_root: Path) -> str:
    """
    Convert a file argument to a repo-relative forward-slash path.
    Accepts both absolute paths and paths already relative to the repo root.
    """
    p = Path(file_arg)
    if p.is_absolute():
        try:
            rel = p.relative_to(repo_root)
        except ValueError:
            # Outside repo — return as-is normalised
            return p.as_posix()
        return rel.as_posix()
    # Already relative — normalise separators only
    return p.as_posix()


def run_check(
    agent: str,
    files: list[str],
    strict: bool,
    repo_root: Path,
    out=None,
    err=None,
) -> int:
    """
    Core logic.  Returns intended exit code.
    *out* and *err* default to sys.stdout / sys.stderr if not supplied.
    """
    if out is None:
        out = sys.stdout
    if err is None:
        err = sys.stderr

    if not files:
        print("ERROR: --files must list at least one file.", file=err)
        return 2

    # Load scope_matcher
    try:
        sm = _import_scope_matcher()
    except (ImportError, FileNotFoundError) as exc:
        print(f"ERROR: cannot load scope_matcher: {exc}", file=err)
        return 2

    # Load manifest
    try:
        manifest = sm.load_manifest(repo_root)
    except FileNotFoundError:
        print(
            f"ERROR: .claude/scope.yaml not found under {repo_root}",
            file=err,
        )
        return 2
    except (ValueError, Exception) as exc:
        print(f"ERROR: failed to parse scope.yaml: {exc}", file=err)
        return 2

    # Validate agent exists
    agents_section = manifest.get("agents", {}) or {}
    valid_agents = list(agents_section.keys()) + ["main_session"]
    if agent not in valid_agents:
        print(
            f"ERROR: agent '{agent}' not found in scope.yaml. "
            f"Known agents: {', '.join(sorted(valid_agents))}",
            file=err,
        )
        return 2

    violations: list[str] = []
    missing_files: list[str] = []
    has_source = False

    for file_arg in files:
        rel = _normalize_rel(file_arg, repo_root)

        # Check existence in --strict mode
        abs_path = Path(file_arg) if Path(file_arg).is_absolute() else repo_root / rel
        if not abs_path.exists():
            if strict:
                missing_files.append(file_arg)
            else:
                print(
                    f"WARNING: file does not exist (treating as new): {file_arg}",
                    file=err,
                )

        # Source-file reminder check
        if _is_source_file(rel):
            has_source = True

        # Scope check
        try:
            allowed = sm.agent_allows(manifest, agent, rel)
        except KeyError:
            # Should not happen since we validated agent above, but be defensive
            print(f"ERROR: agent '{agent}' lookup failed for {rel}", file=err)
            return 2

        if not allowed:
            # Find which agent does own it (for a helpful message)
            owner = None
            for other_agent in agents_section:
                try:
                    if sm.agent_allows(manifest, other_agent, rel):
                        owner = other_agent
                        break
                except KeyError:
                    pass
            owner_msg = f"owned by {owner}" if owner else "not in any agent's allow list"
            violations.append(f"  {rel} — {owner_msg}")

    # Print REMINDER for source files before reporting violations
    if has_source:
        source_files_str = " ".join(
            _normalize_rel(f, repo_root)
            for f in files
            if _is_source_file(_normalize_rel(f, repo_root))
        )
        print(
            f"REMINDER: brief must include "
            f"'pre-commit run --files {source_files_str}' as terminal Rule 3 step.",
            file=out,
        )

    # Report missing-file errors (strict mode)
    for mf in missing_files:
        print(f"ERROR: file does not exist (--strict): {mf}", file=err)

    # Report scope violations
    if violations:
        print(
            f"SCOPE VIOLATION: agent '{agent}' is not allowed to touch:",
            file=err,
        )
        for v in violations:
            print(v, file=err)
        print(
            "NOT dispatchable. Delegate to the correct agent or amend scope.yaml.",
            file=err,
        )

    if violations or missing_files:
        return 1
    return 0


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def run_selftest() -> int:
    """
    Run an embedded test suite.  Exit 0 if all pass, 1 otherwise.
    """
    failures: list[str] = []

    import io

    def check(
        label: str,
        agent: str,
        files: list[str],
        strict: bool,
        expected_exit: int,
        expect_reminder: bool = False,
        repo_root: Path | None = None,
    ) -> None:
        root = repo_root or _REPO_ROOT
        out_buf = io.StringIO()
        err_buf = io.StringIO()
        code = run_check(agent, files, strict, root, out=out_buf, err=err_buf)
        stdout_text = out_buf.getvalue()
        if code != expected_exit:
            failures.append(
                f"[{label}] expected exit {expected_exit}, got {code}\n"
                f"  stdout: {stdout_text!r}\n"
                f"  stderr: {err_buf.getvalue()!r}"
            )
            return
        if expect_reminder and "REMINDER" not in stdout_text:
            failures.append(
                f"[{label}] expected 'REMINDER' in stdout, got: {stdout_text!r}"
            )

    # Case 1: Happy path — security-agent reading a file it owns
    check(
        label="happy-path security-agent",
        agent="security-agent",
        files=["backend/app/infrastructure/config/env.py"],
        strict=False,
        expected_exit=0,
    )

    # Case 2: Scope violation — frontend-agent touching backend file
    check(
        label="scope-violation frontend-agent",
        agent="frontend-agent",
        files=["backend/app/foo.py"],
        strict=False,
        expected_exit=1,
    )

    # Case 3: Source-files reminder — backend-agent touching application code
    check(
        label="source-reminder backend-agent",
        agent="backend-agent",
        files=["backend/app/application/use_cases/x.py"],
        strict=False,
        expected_exit=0,
        expect_reminder=True,
    )

    # Case 4: Config error — unknown agent
    check(
        label="unknown-agent config-error",
        agent="nonexistent-agent",
        files=["foo.py"],
        strict=False,
        expected_exit=2,
    )

    # Case 5 & 6: Missing files — strict vs loose
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_root = Path(tmpdir)
        # Build a minimal scope.yaml
        dot_claude = tmp_root / ".claude"
        dot_claude.mkdir()
        (dot_claude / "scope.yaml").write_text(
            "main_session:\n  allow:\n    - 'planning/**'\n"
            "agents:\n  backend-agent:\n    allow:\n      - 'backend/app/**'\n",
            encoding="utf-8",
        )

        nonexistent = str(tmp_root / "backend" / "app" / "does_not_exist.py")

        # Strict mode: missing file on disk → exit 1
        check(
            label="missing-file strict",
            agent="backend-agent",
            files=[nonexistent],
            strict=True,
            expected_exit=1,
            repo_root=tmp_root,
        )

        # Loose mode: missing file → exit 0 + warning to stderr
        out_buf = __import__("io").StringIO()
        err_buf = __import__("io").StringIO()
        code = run_check(
            "backend-agent",
            [nonexistent],
            strict=False,
            repo_root=tmp_root,
            out=out_buf,
            err=err_buf,
        )
        if code != 0:
            failures.append(
                f"[missing-file loose] expected exit 0, got {code}\n"
                f"  stderr: {err_buf.getvalue()!r}"
            )
        elif "WARNING" not in err_buf.getvalue():
            failures.append(
                f"[missing-file loose] expected 'WARNING' in stderr, "
                f"got: {err_buf.getvalue()!r}"
            )

    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("preflight_dispatch.py selftest: all cases passed.", file=sys.stderr)
    return 0


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    if "--selftest" in sys.argv:
        return run_selftest()

    parser = argparse.ArgumentParser(
        description="Pre-flight scope check before dispatching to a subagent.",
    )
    parser.add_argument("--agent", required=True, help="Target agent name")
    parser.add_argument(
        "--files",
        nargs="+",
        metavar="FILE",
        required=True,
        help="Files the brief plans to touch",
    )
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--strict",
        action="store_true",
        default=False,
        help="Error on non-existent files (default: warn only)",
    )
    mode.add_argument(
        "--loose",
        action="store_true",
        default=False,
        help="Warn but don't error on non-existent files (default)",
    )

    args = parser.parse_args()
    strict = args.strict  # --loose is the default (strict=False)

    return run_check(args.agent, args.files, strict, _REPO_ROOT)


if __name__ == "__main__":
    sys.exit(main())
