#!/usr/bin/env python3
"""
commit_msg_simplify_gate.py — commit-msg hook enforcing a Simplify: decision.

If the staged commit touches any file under backend/app/** or frontend/src/**,
OR if a staged diff of any planning/**/PLAN.md moves a sub-phase status from
"In progress" to "Complete", the commit body must contain one of:

  Simplify: ran, clean
  Simplify: ran, <N> findings addressed in <file>:<line>, ...
  Simplify: waived — <reason of 10+ chars>

Pure config / pure docs commits (no source files, no plan status changes) are exempt.

Usage (git hook):
  python scripts/hooks/commit_msg_simplify_gate.py <commit-msg-file>

Exit codes:
  0 — accepted
  1 — rejected (missing or malformed Simplify: line)

Supports --selftest: runs 4 assertions and exits 0/1.
"""

import re
import subprocess
import sys
import tempfile
from pathlib import Path

# Patterns that, if matched by any staged file path, require Simplify:.
SOURCE_PATTERNS: list[re.Pattern[str]] = [
    re.compile(r"^backend/app/"),
    re.compile(r"^frontend/src/"),
]

# Pattern for plan files
PLAN_FILE_PATTERN = re.compile(r"^planning/.+/PLAN\.md$")

# Regex to detect a sub-phase status transition from "In progress" to "Complete"
# in a unified diff hunk.  Matches lines like:
#   -| 00c | ... | In progress |
#   +| 00c | ... | Complete    |
# (simplified — we look for removal of "In progress" and addition of "Complete"
#  within the same diff context, which is sufficient for our use case.)
STATUS_TRANSITION_RE = re.compile(
    r"^\+.*\|\s*Complete\s*\|",
    re.MULTILINE,
)
STATUS_TRANSITION_REMOVED_RE = re.compile(
    r"^-.*\|\s*In progress\s*\|",
    re.MULTILINE,
)

# Valid Simplify: formats (any one suffices)
SIMPLIFY_PATTERNS: list[re.compile] = [  # type: ignore[valid-type]
    re.compile(r"Simplify:\s+ran,\s+clean", re.IGNORECASE),
    re.compile(r"Simplify:\s+ran,\s+\d+\s+findings", re.IGNORECASE),
    re.compile(r"Simplify:\s+waived\s+[—\-–]\s+.{10,}", re.IGNORECASE),
]


def get_staged_files() -> list[str]:
    """Return a list of staged file paths (relative to repo root)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True,
        )
        return [line for line in result.stdout.splitlines() if line.strip()]
    except subprocess.CalledProcessError:
        return []


def get_staged_diff_for_file(path: str) -> str:
    """Return the unified diff for a specific staged file."""
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--", path],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return ""


def commit_touches_source(staged_files: list[str]) -> bool:
    """Return True if any staged file matches a source pattern."""
    for f in staged_files:
        for pattern in SOURCE_PATTERNS:
            if pattern.match(f):
                return True
    return False


def commit_completes_subphase(staged_files: list[str]) -> bool:
    """Return True if any staged PLAN.md diff moves a sub-phase to Complete."""
    for f in staged_files:
        if not PLAN_FILE_PATTERN.match(f):
            continue
        diff = get_staged_diff_for_file(f)
        if STATUS_TRANSITION_RE.search(diff) and STATUS_TRANSITION_REMOVED_RE.search(diff):
            return True
    return False


def has_valid_simplify(msg: str) -> bool:
    """Return True if the commit message body contains a valid Simplify: line."""
    for pattern in SIMPLIFY_PATTERNS:
        if pattern.search(msg):
            return True
    return False


def check_commit_msg(commit_msg_file: str) -> int:
    """
    Main check logic.  Returns 0 (accept) or 1 (reject).
    """
    try:
        msg = Path(commit_msg_file).read_text(encoding="utf-8")
    except OSError as exc:
        print(f"commit_msg_simplify_gate: cannot read commit message file: {exc}", file=sys.stderr)
        return 1

    staged = get_staged_files()

    if not commit_touches_source(staged) and not commit_completes_subphase(staged):
        # Config-only / docs-only commit — exempt
        return 0

    if has_valid_simplify(msg):
        return 0

    print(
        "BLOCKED: This commit touches source files and requires a Simplify: decision.\n"
        "Add one of the following lines to your commit message body:\n"
        "\n"
        "  Simplify: ran, clean\n"
        "  Simplify: ran, <N> findings addressed in <file>:<line>, ...\n"
        "  Simplify: waived — <reason of at least 10 characters>\n"
        "\n"
        "Pure config or pure docs commits are exempt from this requirement.",
        file=sys.stderr,
    )
    return 1


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def run_selftest() -> int:
    """Run 4 assertions.  Returns 0 on all pass, 1 on any failure."""
    import types

    failures: list[str] = []

    # We test check_commit_msg by injecting fake staged-file functions.
    # We do this by temporarily replacing the module-level functions in the
    # current module (referenced via sys.modules or the globals dict).
    import sys as _sys
    _module = _sys.modules[__name__]

    original_get_staged = _module.get_staged_files  # type: ignore[attr-defined]
    original_completes = _module.commit_completes_subphase  # type: ignore[attr-defined]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)

        def write_msg(name: str, body: str) -> str:
            p = tmp / name
            p.write_text(body, encoding="utf-8")
            return str(p)

        try:
            # (a) Source-touching commit missing Simplify: → exit 1
            _module.get_staged_files = lambda: ["backend/app/main.py"]  # type: ignore[attr-defined]
            _module.commit_completes_subphase = lambda _: False  # type: ignore[attr-defined]

            msg_a = write_msg("msg_a.txt", "Fix: something\n\nDid stuff.")
            code = check_commit_msg(msg_a)
            if code != 1:
                failures.append(f"(a) expected 1, got {code}")

            # (b) Same with `Simplify: ran, clean` → exit 0
            msg_b = write_msg("msg_b.txt", "Fix: something\n\nDid stuff.\n\nSimplify: ran, clean")
            code = check_commit_msg(msg_b)
            if code != 0:
                failures.append(f"(b) expected 0, got {code}")

            # (c) Same with waived → exit 0
            msg_c = write_msg(
                "msg_c.txt",
                "Fix: something\n\nDid stuff.\n\nSimplify: waived — config-only preview no logic changed",
            )
            code = check_commit_msg(msg_c)
            if code != 0:
                failures.append(f"(c) expected 0, got {code}")

            # (d) Config-only commit → exit 0 regardless of no Simplify:
            _module.get_staged_files = lambda: ["backend/pyproject.toml", ".github/workflows/ci.yml"]  # type: ignore[attr-defined]
            _module.commit_completes_subphase = lambda _: False  # type: ignore[attr-defined]

            msg_d = write_msg("msg_d.txt", "chore: update deps\n\nNo logic changes.")
            code = check_commit_msg(msg_d)
            if code != 0:
                failures.append(f"(d) expected 0 for config-only commit, got {code}")

        finally:
            _module.get_staged_files = original_get_staged  # type: ignore[attr-defined]
            _module.commit_completes_subphase = original_completes  # type: ignore[attr-defined]

    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("commit_msg_simplify_gate.py selftest: all 4 assertions passed.")
    return 0


def main() -> int:
    if "--selftest" in sys.argv:
        return run_selftest()

    if len(sys.argv) < 2:
        print(
            "Usage: commit_msg_simplify_gate.py <commit-msg-file>",
            file=sys.stderr,
        )
        return 1

    return check_commit_msg(sys.argv[1])


if __name__ == "__main__":
    sys.exit(main())
