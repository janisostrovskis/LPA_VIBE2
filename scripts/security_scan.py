#!/usr/bin/env python3
"""
security_scan.py — Regex-based hardcoded-secret scanner for the LPA project.

Scans every file tracked by Git (via `git ls-files`) for high-confidence
secret patterns.  Binary files are skipped.  Certain paths are exempt.
Lines annotated with `# pragma: allowlist secret` are skipped.

Exit codes:
  0 — no secrets found
  1 — one or more secrets found
  2 — internal error

Supports --selftest: writes a temp file containing `AKIAIOSFODNN7EXAMPLE`,
runs the pattern check against it, and asserts exit code 1.
Cleans up via tempfile.TemporaryDirectory.
"""

import argparse
import re
import subprocess
import sys
import tempfile
from pathlib import Path

# ---------------------------------------------------------------------------
# Secret patterns — each tuple is (name, compiled_regex).
# ---------------------------------------------------------------------------
_RAW_PATTERNS: list[tuple[str, str]] = [
    ("AWS access key", r"AKIA[0-9A-Z]{16}"),
    (
        "AWS secret",
        r"(?i)aws(.{0,20})?(secret|access).{0,5}['\"][0-9a-zA-Z/+]{40}['\"]",
    ),
    ("Stripe live", r"sk_live_[0-9a-zA-Z]{24,}"),
    ("Stripe test", r"sk_test_[0-9a-zA-Z]{24,}"),
    ("GitHub token", r"gh[pousr]_[A-Za-z0-9]{36,}"),
    (
        "Private key",
        r"-----BEGIN (RSA |EC |OPENSSH |DSA |)PRIVATE KEY-----",
    ),
    ("Generic password", r"(?i)password\s*=\s*['\"][^'\"]{6,}['\"]"),
    ("JWT secret", r"(?i)jwt[_-]?secret\s*=\s*['\"][^'\"]{8,}['\"]"),
    ("Hardcoded DB URL", r"postgres(ql)?://[^:\s]+:[^@\s]+@"),
]

PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    (name, re.compile(pattern)) for name, pattern in _RAW_PATTERNS
]

# ---------------------------------------------------------------------------
# Exempt file paths (relative, forward-slash).
# Files whose path string starts with one of these prefixes (or matches
# exactly) are skipped.  The script itself is exempt because its own pattern
# strings would otherwise self-match.
# ---------------------------------------------------------------------------
EXEMPT_PREFIXES: tuple[str, ...] = (
    ".env.example",
    ".mcp.json",       # Local MCP server config — development credentials only
    "docs/",
    "planning/",
    ".claude/",
    "scripts/security_scan.py",
)

ALLOWLIST_MARKER = "# pragma: allowlist secret"
BINARY_PROBE_BYTES = 1024


def is_exempt(rel_path: str) -> bool:
    """Return True if the path should be skipped."""
    for prefix in EXEMPT_PREFIXES:
        if rel_path == prefix or rel_path.startswith(prefix):
            return True
    return False


def is_binary(path: Path) -> bool:
    """Return True if the file appears to be binary (null byte in first 1 KiB)."""
    try:
        with path.open("rb") as fh:
            chunk = fh.read(BINARY_PROBE_BYTES)
        return b"\x00" in chunk
    except OSError:
        return False


def scan_content(
    content: str,
    path: Path,
) -> list[tuple[int, str, str]]:
    """
    Scan file content for secret patterns.

    Returns a list of (lineno, pattern_name, snippet) tuples for each match.
    Snippet is truncated to 40 characters.
    Lines containing ALLOWLIST_MARKER are skipped.
    """
    findings: list[tuple[int, str, str]] = []
    for lineno, line in enumerate(content.splitlines(), start=1):
        if ALLOWLIST_MARKER in line:
            continue
        for name, pattern in PATTERNS:
            match = pattern.search(line)
            if match:
                snippet = match.group(0)[:40]
                findings.append((lineno, name, snippet))
    return findings


def get_tracked_files() -> list[str]:
    """
    Return a list of file paths tracked by Git (relative, forward-slash).

    Uses subprocess with a list of args for cross-platform safety.
    Raises subprocess.CalledProcessError on failure.
    """
    result = subprocess.run(
        ["git", "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    return [line for line in result.stdout.splitlines() if line.strip()]


def run_scan(project_root: Path) -> int:
    """
    Enumerate tracked files, apply exemptions, scan each for secrets.

    Returns 0 (clean) or 1 (findings).
    """
    tracked = get_tracked_files()
    found_any = False

    for rel_path_str in tracked:
        if is_exempt(rel_path_str):
            continue

        full_path = project_root / Path(rel_path_str)

        if not full_path.is_file():
            continue

        if is_binary(full_path):
            continue

        try:
            content = full_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            print(f"WARNING: could not read {rel_path_str}: {exc}", file=sys.stderr)
            continue

        findings = scan_content(content, full_path)
        for lineno, name, snippet in findings:
            print(f"FAIL {rel_path_str}:{lineno} [{name}] {snippet!r}")
            found_any = True

    return 1 if found_any else 0


def selftest() -> int:
    """
    Self-test: write a file containing a known AWS access key pattern,
    scan it, and assert exactly one finding is returned.

    Returns 1 on pass (finding correctly detected) or 2 on failure.
    """
    print("Running security_scan.py --selftest ...")

    with tempfile.TemporaryDirectory() as tmp_str:
        tmp = Path(tmp_str)
        test_file = tmp / "fake_secret.py"
        # AKIAIOSFODNN7EXAMPLE is the canonical AWS documentation example key.
        test_file.write_text(
            'API_KEY = "AKIAIOSFODNN7EXAMPLE"\n',
            encoding="utf-8",
        )

        content = test_file.read_text(encoding="utf-8")
        findings = scan_content(content, test_file)

        if findings:
            lineno, name, snippet = findings[0]
            print(
                f"SELFTEST PASS: {test_file}:{lineno} [{name}] {snippet!r} detected."
            )
            return 1  # Caller expects exit 1 from selftest
        else:
            print("SELFTEST FAIL: expected a finding but got none.", file=sys.stderr)
            return 2


def main() -> int:
    """Parse arguments and dispatch to scan or selftest."""
    parser = argparse.ArgumentParser(
        description="Scan tracked files for hardcoded secrets.",
    )
    parser.add_argument(
        "--selftest",
        action="store_true",
        help="Run a self-test with a synthetic secret file and exit 1 on success.",
    )
    args = parser.parse_args()

    if args.selftest:
        return selftest()

    return run_scan(Path.cwd())


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(2)
    except Exception as exc:  # noqa: BLE001
        print(f"INTERNAL ERROR: {exc}", file=sys.stderr)
        sys.exit(2)
