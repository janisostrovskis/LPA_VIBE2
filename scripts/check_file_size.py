#!/usr/bin/env python3
"""
check_file_size.py — Enforce per-file line-count limits for the LPA project.

Exit codes:
  0 — no violations found
  1 — one or more files exceed the hard limit (HARD=2000 lines)
  2 — internal error (unexpected exception)

Warns to stderr (non-failing) for files between WARN=1500 and HARD=2000 lines.

Exempt paths: any file whose path contains an element from EXEMPT_PARTS is skipped.
Scanned extensions: EXTENSIONS  (.py, .ts, .tsx)
Scanned roots: SCAN_ROOTS (backend/, frontend/)

Supports --selftest: writes a synthetic 2001-line temp file, points the scan
at it, and asserts exit code 1. Cleans up via tempfile.TemporaryDirectory.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

EXEMPT_PARTS: set[str] = {
    "alembic/versions",
    "__pycache__",
    ".next",
    "node_modules",
    "dist",
    "build",
    ".venv",
    ".git",
}

EXTENSIONS: set[str] = {".py", ".ts", ".tsx"}
SCAN_ROOTS: list[str] = ["backend", "frontend"]
WARN: int = 1500
HARD: int = 2000


def is_exempt(path: Path) -> bool:
    """Return True if any part of the path matches an exempt segment."""
    parts_str = "/".join(path.parts)
    for exempt in EXEMPT_PARTS:
        if exempt in parts_str:
            return True
    return False


def count_lines(path: Path) -> int:
    """Return the number of lines in a file (min 1 for non-empty files)."""
    content = path.read_text(encoding="utf-8", errors="replace")
    return content.count("\n") + 1


def scan_root(root: Path) -> tuple[list[tuple[Path, int]], list[tuple[Path, int]]]:
    """
    Scan a single root directory.

    Returns (violations, warnings) where each element is (path, line_count).
    """
    violations: list[tuple[Path, int]] = []
    warnings: list[tuple[Path, int]] = []

    if not root.is_dir():
        return violations, warnings

    for ext in EXTENSIONS:
        for path in root.rglob(f"*{ext}"):
            if is_exempt(path):
                continue
            lines = count_lines(path)
            if lines > HARD:
                violations.append((path, lines))
            elif lines > WARN:
                warnings.append((path, lines))

    return violations, warnings


def run_scan(project_root: Path) -> int:
    """
    Run the full file-size scan against SCAN_ROOTS under project_root.

    Returns exit code: 0 (clean), 1 (violations), 2 (internal error).
    """
    all_violations: list[tuple[Path, int]] = []
    all_warnings: list[tuple[Path, int]] = []

    for root_name in SCAN_ROOTS:
        root = project_root / root_name
        violations, warnings = scan_root(root)
        all_violations.extend(violations)
        all_warnings.extend(warnings)

    for path, lines in all_warnings:
        print(
            f"WARNING {path} — {lines} lines (approaching {HARD}-line limit)",
            file=sys.stderr,
        )

    for path, lines in all_violations:
        print(f"FAIL {path} — {lines} lines exceeds hard limit of {HARD}")

    if all_violations:
        return 1
    return 0


def selftest() -> int:
    """
    Self-test: create a synthetic 2001-line file in a temp directory, run the
    scan against it, and assert exit code 1.  Cleans up on exit.

    Returns 0 if the self-test passes, 2 if it fails.
    """
    print("Running check_file_size.py --selftest ...")

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)

        # Mirror the SCAN_ROOTS structure so the scanner can find the file.
        backend_dir = tmp / "backend"
        backend_dir.mkdir()
        big_file = backend_dir / "big_module.py"

        # Write 2001 lines: one header comment + 2000 blank lines.
        lines = ["# synthetic oversized file for selftest\n"] + ["\n"] * 2000
        big_file.write_text("".join(lines), encoding="utf-8")

        actual_lines = count_lines(big_file)
        if actual_lines < HARD + 1:
            print(
                f"SELFTEST INTERNAL ERROR: synthetic file has {actual_lines} lines, "
                f"expected >{HARD}",
                file=sys.stderr,
            )
            return 2

        exit_code = run_scan(tmp)
        if exit_code == 1:
            print("SELFTEST PASS: violation correctly detected.")
            return 1  # Caller expects exit 1 from this selftest
        else:
            print(
                f"SELFTEST FAIL: expected exit 1, got {exit_code}",
                file=sys.stderr,
            )
            return 2


def main() -> int:
    """Parse arguments and dispatch to scan or selftest."""
    parser = argparse.ArgumentParser(
        description="Enforce per-file line-count limits.",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path.cwd(),
        help="Project root directory (default: cwd)",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run a self-test with a synthetic oversized file and exit 1 on success.",
    )
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    return run_scan(args.root)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
    except Exception as exc:  # noqa: BLE001
        print(f"INTERNAL ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
