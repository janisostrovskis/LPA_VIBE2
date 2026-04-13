#!/usr/bin/env python3
"""
check_handoff_log.py — Validate HANDOFF_LOG.md files against the required schema.

Schema per section (each ## entry):
  - **Task:** one-line summary
  - **Scope (files changed):** list of paths
  - **Skills invoked:** list of `skill-name` — PASS | FAIL | N/A (reason)
  - **Rule 3 verification:** list of `command` → exit N
  - **Result:** HANDOFF COMPLETE — PASS | FAIL

Rules:
  - All five required sub-sections must be present.
  - Result line must match HANDOFF COMPLETE — (PASS|FAIL).
  - For frontend-agent entries touching frontend/src/app/** or frontend/src/components/**:
    `frontend-design` must appear with PASS.
  - For any agent entry touching source files (not pure config):
    `simplify` must appear with PASS or an explicit `waived — <reason>`.
  - For any agent entry dated 2026-04-09 or later touching source files:
    the Rule 3 verification section MUST contain a backtick-wrapped command
    starting with `pre-commit run` (--all-files or --files <anything>).
  - For any agent entry dated 2026-04-09 or later touching source files that claims
    `simplify` — PASS (not waived): a simplify-receipt artifact file must exist at
    <phase_dir>/simplify-receipts/<subphase>-<agent>.md where phase_dir is the
    directory containing HANDOFF_LOG.md. Skipped when log_path is None (inline tests).
  - Entries with `retrofit: true` in Notes are exempt from the skills/simplify checks
    and from the pre-commit run check (still require section structure).
  - Entries dated before 2026-04-09 are exempt from the pre-commit run check and the
    simplify-receipt artifact check.

Accepts --bootstrap flag: relaxes all strict checks (used during initial 00d commit
when check_handoff_log.py itself is being introduced and no entry for 00d exists yet).

Exit codes:
  0 — valid
  1 — validation violations found
  2 — schema / parse error

Supports --selftest.
"""

from __future__ import annotations

import re
import sys
import tempfile
from datetime import date
from pathlib import Path

REQUIRED_SUBSECTIONS = [
    "Task:",
    "Scope (files changed):",
    "Skills invoked:",
    "Rule 3 verification:",
    "Result:",
]

RESULT_PATTERN = re.compile(r"HANDOFF COMPLETE\s*[—\-–]\s*(PASS|FAIL)", re.IGNORECASE)

# Source file patterns (non-exhaustive) — used to decide if simplify is required
SOURCE_PATTERNS = [
    re.compile(r"^backend/app/"),
    re.compile(r"^frontend/src/"),
]
CONFIG_ONLY_PATTERNS = [
    re.compile(r"^backend/pyproject\.toml$"),
    re.compile(r"^\.github/"),
    re.compile(r"^scripts/"),
    re.compile(r"^\.pre-commit-config\.yaml$"),
    re.compile(r"^\.claude/"),
    re.compile(r"^docker-compose\.yml$"),
    re.compile(r"^frontend/tsconfig\.json$"),
    re.compile(r"^frontend/package\.json$"),
]

FRONTEND_APP_PATTERNS = [
    re.compile(r"^frontend/src/app/"),
    re.compile(r"^frontend/src/components/"),
]

# Entries dated on or after this date must include a `pre-commit run` command
# in their Rule 3 verification section when they touch source files.
PRECOMMIT_MANDATE_DATE = date(2026, 4, 9)

# Matches a backtick-wrapped pre-commit run command anywhere in Rule 3 text.
PRECOMMIT_RUN_PATTERN = re.compile(
    r"`pre-commit run(?:\s+--all-files|\s+--files\s+[^`]+)?`",
)


def is_source_file(path: str) -> bool:
    for pat in SOURCE_PATTERNS:
        if pat.match(path.strip()):
            return True
    return False


def is_frontend_app_file(path: str) -> bool:
    for pat in FRONTEND_APP_PATTERNS:
        if pat.match(path.strip()):
            return True
    return False


def parse_entries(content: str) -> list[dict]:
    """
    Split HANDOFF_LOG.md into entries at each '## ' heading.
    Returns list of dicts: {header, body, line_no}
    """
    entries: list[dict] = []
    lines = content.splitlines()
    current_header: str | None = None
    current_body: list[str] = []
    current_line: int = 0

    for i, line in enumerate(lines, 1):
        if line.startswith("## "):
            if current_header is not None:
                entries.append({
                    "header": current_header,
                    "body": "\n".join(current_body),
                    "line_no": current_line,
                })
            current_header = line[3:].strip()
            current_body = []
            current_line = i
        elif current_header is not None:
            current_body.append(line)

    if current_header is not None:
        entries.append({
            "header": current_header,
            "body": "\n".join(current_body),
            "line_no": current_line,
        })

    return entries


def _parse_entry_date(header: str) -> date | None:
    """
    Parse the ISO date from a header of the form '[subphase] — [agent] — [YYYY-MM-DD]'.
    Looks for a YYYY-MM-DD pattern anywhere in the header to avoid splitting on
    hyphens within the date itself.
    Returns None if parsing fails.
    """
    match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", header)
    if not match:
        return None
    try:
        return date.fromisoformat(match.group(1))
    except ValueError:
        return None


def validate_entry(
    entry: dict,
    bootstrap: bool,
    log_path: Path | None = None,
) -> list[str]:
    """
    Validate a single log entry.  Returns a list of violation messages (empty = clean).

    log_path: path to the HANDOFF_LOG.md being validated.  When provided, the
    simplify-receipt artifact check is performed.  When None (e.g., inline selftest
    strings without a disk fixture), the artifact check is skipped.
    """
    violations: list[str] = []
    body = entry["body"]
    header = entry["header"]
    line_no = entry["line_no"]
    prefix = f"Entry '{header}' (line {line_no})"

    is_retrofit = bool(
        re.search(r"retrofit:\s*true", body, re.IGNORECASE)
        or re.search(r"`?retrofit:\s*true`?", body, re.IGNORECASE)
        or "retrofit: true" in body.lower()
    )

    # Always require section structure
    for section in REQUIRED_SUBSECTIONS:
        if section not in body:
            violations.append(f"{prefix}: missing required sub-section '{section}'")

    if violations:
        # Can't do deeper checks without structure
        return violations

    # Check Result line
    if not RESULT_PATTERN.search(body):
        violations.append(
            f"{prefix}: Result line must match 'HANDOFF COMPLETE — PASS|FAIL'"
        )

    # Skip strict checks for retrofit entries or bootstrap mode
    if is_retrofit or bootstrap:
        return violations

    # Extract scope file list
    scope_match = re.search(
        r"\*\*Scope \(files changed\):\*\*(.*?)(?=\n\*\*|\Z)",
        body,
        re.DOTALL,
    )
    scope_files: list[str] = []
    if scope_match:
        scope_block = scope_match.group(1)
        for line in scope_block.splitlines():
            stripped = line.strip()
            if stripped.startswith("-"):
                path = stripped[1:].strip().strip("`")
                if path:
                    scope_files.append(path)

    # Extract skills block
    skills_match = re.search(
        r"\*\*Skills invoked:\*\*(.*?)(?=\n\*\*|\Z)",
        body,
        re.DOTALL,
    )
    skills_text = skills_match.group(1) if skills_match else ""

    # Determine agent from header (format: "[sub-phase] — [agent] — [date]")
    parts = re.split(r"\s*[—\-–]\s*", header)
    agent_name = parts[1].strip().lower() if len(parts) >= 2 else ""

    # frontend-agent entries touching app/components → frontend-design PASS required
    if "frontend" in agent_name:
        needs_design_skill = any(is_frontend_app_file(f) for f in scope_files)
        if needs_design_skill:
            if not re.search(r"`?frontend-design`?\s*[—\-–]\s*PASS", skills_text, re.IGNORECASE):
                violations.append(
                    f"{prefix}: frontend-agent touching frontend/src/app/** or "
                    f"frontend/src/components/** requires 'frontend-design — PASS' in Skills invoked"
                )

    # Source-touching entries → simplify PASS or waived required
    has_source = any(is_source_file(f) for f in scope_files)
    if has_source:
        simplify_ok = bool(
            re.search(r"`?simplify`?\s*[—\-–]\s*PASS", skills_text, re.IGNORECASE)
            or re.search(r"`?simplify`?\s*[—\-–]\s*N/A\s*\(waived", skills_text, re.IGNORECASE)
            or re.search(r"`?simplify`?\s*[—\-–]\s*waived", skills_text, re.IGNORECASE)
        )
        if not simplify_ok:
            violations.append(
                f"{prefix}: entry touches source files but 'simplify' is not listed "
                f"with PASS or waived in Skills invoked"
            )

    # Source-touching entries dated 2026-04-09 or later → pre-commit run required
    # Entries with retrofit: true are exempt.  Entries before the mandate date are exempt.
    # If the date cannot be parsed, treat as NOT exempt (fail closed).
    if has_source:
        entry_date = _parse_entry_date(header)
        precommit_required = (
            entry_date is None or entry_date >= PRECOMMIT_MANDATE_DATE
        )
        if precommit_required:
            rule3_match = re.search(
                r"\*\*Rule 3 verification:\*\*(.*?)(?=\n\*\*|\Z)",
                body,
                re.DOTALL,
            )
            rule3_text = rule3_match.group(1) if rule3_match else ""
            if not PRECOMMIT_RUN_PATTERN.search(rule3_text):
                violations.append(
                    f"{prefix}: entry dated {entry_date} touches source files but "
                    f"Rule 3 verification does not contain a backtick-wrapped "
                    f"`pre-commit run` command (mandatory for entries dated "
                    f"{PRECOMMIT_MANDATE_DATE} or later)"
                )

        # Source-touching entries dated 2026-04-09 or later that claim
        # `simplify` — PASS (not waived, not N/A) must have a matching
        # simplify-receipt artifact file on disk.
        # Skipped when log_path is None (inline selftest without disk fixture).
        if log_path is not None and precommit_required:
            simplify_pass = bool(
                re.search(
                    r"`?simplify`?\s*[—\-–]\s*PASS",
                    skills_text,
                    re.IGNORECASE,
                )
            )
            simplify_waived = bool(
                re.search(
                    r"`?simplify`?\s*[—\-–]\s*(?:N/A\s*\(waived|waived)",
                    skills_text,
                    re.IGNORECASE,
                )
            )
            if simplify_pass and not simplify_waived:
                # Derive subphase and agent from header.
                # Header format: "[subphase] — [agent] — [date]"
                # Split ONLY on em-dash / en-dash (not plain hyphens) so that
                # agent names like "devops-agent" are not fragmented.
                em_parts = re.split(r"\s*[—–]\s*", header)
                subphase = em_parts[0].strip() if len(em_parts) >= 1 else "unknown"
                agent = em_parts[1].strip().lower() if len(em_parts) >= 2 else "unknown"
                phase_dir = log_path.parent
                expected_artifact = (
                    phase_dir / "simplify-receipts" / f"{subphase}-{agent}.md"
                )
                if not expected_artifact.exists():
                    violations.append(
                        f"{prefix}: entry dated {entry_date} claims 'simplify — PASS' "
                        f"but missing artifact: {expected_artifact}"
                    )

    return violations


def validate_log(
    content: str,
    bootstrap: bool = False,
    log_path: Path | None = None,
) -> tuple[int, list[str]]:
    """
    Validate full HANDOFF_LOG content.
    Returns (exit_code, [violation_messages]).
    exit_code: 0 = clean, 1 = violations, 2 = schema error.

    log_path: path to the HANDOFF_LOG.md file.  When provided, the simplify-receipt
    artifact check is performed.  When None (e.g., inline selftest strings), skipped.
    """
    if not content.strip():
        return 0, []

    try:
        entries = parse_entries(content)
    except Exception as exc:
        return 2, [f"Schema parse error: {exc}"]

    all_violations: list[str] = []
    for entry in entries:
        violations = validate_entry(entry, bootstrap=bootstrap, log_path=log_path)
        all_violations.extend(violations)

    if all_violations:
        return 1, all_violations
    return 0, []


def find_handoff_logs(repo_root: Path) -> list[Path]:
    """Find all HANDOFF_LOG.md files under planning/."""
    planning_dir = repo_root / "planning"
    if not planning_dir.exists():
        return []
    return list(planning_dir.rglob("HANDOFF_LOG.md"))


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------

def run_selftest() -> int:
    failures: list[str] = []

    # A valid entry (non-retrofit, no source files)
    valid_entry = """## 00d — devops-agent — 2026-04-08

- **Task:** Set up runtime enforcement infrastructure
- **Scope (files changed):**
  - `.claude/scope.yaml`
  - `scripts/hooks/pretool_scope_guard.py`
  - `.pre-commit-config.yaml`
- **Skills invoked:**
  - `update-config` — PASS
- **Rule 3 verification:**
  - `python -c "import yaml; yaml.safe_load(open('.claude/scope.yaml'))"` → exit 0
- **Result:** HANDOFF COMPLETE — PASS
- **Notes:** Config-only deliverable.
"""

    code, violations = validate_log(valid_entry)
    if code != 0:
        failures.append(f"valid entry: expected 0, got {code}; violations: {violations}")

    # Missing Skills invoked section → should fail
    missing_skills = """## 00x — devops-agent — 2026-04-08

- **Task:** Something
- **Scope (files changed):**
  - `scripts/foo.py`
- **Rule 3 verification:**
  - `python scripts/foo.py` → exit 0
- **Result:** HANDOFF COMPLETE — PASS
"""
    code, violations = validate_log(missing_skills)
    if code != 1:
        failures.append(f"missing skills: expected 1, got {code}")

    # Retrofit entry with missing skills → should pass (retrofit exempt)
    retrofit_missing = """## 00a — devops-agent — 2026-01-01

- **Task:** Foundation setup
- **Scope (files changed):**
  - `backend/app/main.py`
- **Skills invoked:**
  - N/A — retrofit entry
- **Rule 3 verification:**
  - N/A
- **Result:** HANDOFF COMPLETE — PASS
- **Notes:** retrofit: true — historical entry, pre-gate
"""
    code, violations = validate_log(retrofit_missing)
    if code != 0:
        failures.append(f"retrofit entry: expected 0, got {code}; violations: {violations}")

    # Source-touching entry missing simplify → should fail
    source_no_simplify = """## 00y — backend-agent — 2026-04-08

- **Task:** Add domain model
- **Scope (files changed):**
  - `backend/app/domain/entities/member.py`
- **Skills invoked:**
  - `update-config` — N/A (no config touched)
- **Rule 3 verification:**
  - `python -m pytest` → exit 0
- **Result:** HANDOFF COMPLETE — PASS
"""
    code, violations = validate_log(source_no_simplify)
    if code != 1:
        failures.append(f"source-no-simplify: expected 1, got {code}")

    # pre-commit run mandate: source entry dated 2026-04-10 (after cutoff) without
    # pre-commit run line → must fail
    precommit_missing = """## 00h — devops-agent — 2026-04-10

- **Task:** Add new feature
- **Scope (files changed):**
  - `backend/app/domain/entities/member.py`
- **Skills invoked:**
  - `simplify` — PASS
- **Rule 3 verification:**
  - `python -m pytest` → exit 0
- **Result:** HANDOFF COMPLETE — PASS
"""
    code, violations = validate_log(precommit_missing)
    if code != 1:
        failures.append(
            f"precommit-missing (post-cutoff): expected 1, got {code}; "
            f"violations: {violations}"
        )

    # pre-commit run mandate: source entry dated 2026-04-10 WITH pre-commit run → pass
    precommit_present = """## 00h — devops-agent — 2026-04-10

- **Task:** Add new feature
- **Scope (files changed):**
  - `backend/app/domain/entities/member.py`
- **Skills invoked:**
  - `simplify` — PASS
- **Rule 3 verification:**
  - `python -m pytest` → exit 0
  - `pre-commit run --files backend/app/domain/entities/member.py` → exit 0
- **Result:** HANDOFF COMPLETE — PASS
"""
    code, violations = validate_log(precommit_present)
    if code != 0:
        failures.append(
            f"precommit-present (post-cutoff): expected 0, got {code}; "
            f"violations: {violations}"
        )

    # pre-commit run mandate: source entry dated 2026-04-07 (before cutoff) without
    # pre-commit run line → must pass (retroactive exemption)
    precommit_old_entry = """## 00z — devops-agent — 2026-04-07

- **Task:** Old work before the mandate
- **Scope (files changed):**
  - `backend/app/domain/entities/member.py`
- **Skills invoked:**
  - `simplify` — PASS
- **Rule 3 verification:**
  - `python -m pytest` → exit 0
- **Result:** HANDOFF COMPLETE — PASS
"""
    code, violations = validate_log(precommit_old_entry)
    if code != 0:
        failures.append(
            f"precommit-old-entry (pre-cutoff): expected 0, got {code}; "
            f"violations: {violations}"
        )

    # --- Simplify-receipt artifact checks (3 new cases) ---

    # Shared entry text: post-cutoff, source files, simplify — PASS (no waiver).
    # Needs a pre-commit run line too (to pass the existing mandate check).
    artifact_entry = """## 00h — devops-agent — 2026-04-10

- **Task:** Add domain feature
- **Scope (files changed):**
  - `backend/app/domain/entities/member.py`
- **Skills invoked:**
  - `simplify` — PASS
- **Rule 3 verification:**
  - `python -m pytest` → exit 0
  - `pre-commit run --files backend/app/domain/entities/member.py` → exit 0
- **Result:** HANDOFF COMPLETE — PASS
"""

    # Case a: artifact does NOT exist → exit 1
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_log = Path(tmpdir) / "HANDOFF_LOG.md"
        tmp_log.write_text(artifact_entry, encoding="utf-8")
        code, violations = validate_log(
            artifact_entry, log_path=tmp_log
        )
        if code != 1:
            failures.append(
                f"artifact-missing: expected 1, got {code}; violations: {violations}"
            )
        else:
            # Confirm the violation mentions the artifact filename (path-separator
            # agnostic — avoids Windows vs POSIX slash mismatch in the check).
            expected_fragment = "00h-devops-agent.md"
            if not any(expected_fragment in v for v in violations):
                failures.append(
                    f"artifact-missing: violation text missing '{expected_fragment}'; "
                    f"got: {violations}"
                )

    # Case b: artifact file pre-created → exit 0
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_log = Path(tmpdir) / "HANDOFF_LOG.md"
        tmp_log.write_text(artifact_entry, encoding="utf-8")
        receipts_dir = Path(tmpdir) / "simplify-receipts"
        receipts_dir.mkdir()
        (receipts_dir / "00h-devops-agent.md").write_text(
            "simplify receipt", encoding="utf-8"
        )
        code, violations = validate_log(
            artifact_entry, log_path=tmp_log
        )
        if code != 0:
            failures.append(
                f"artifact-present: expected 0, got {code}; violations: {violations}"
            )

    # Case c: log_path=None → artifact check skipped → exit 0
    code, violations = validate_log(artifact_entry, log_path=None)
    if code != 0:
        failures.append(
            f"artifact-no-log-path: expected 0 (check skipped), got {code}; "
            f"violations: {violations}"
        )

    if failures:
        print("SELFTEST FAILED:", file=sys.stderr)
        for f in failures:
            print(f"  {f}", file=sys.stderr)
        return 1
    print("check_handoff_log.py selftest: all assertions passed.")
    return 0


def main() -> int:
    bootstrap = "--bootstrap" in sys.argv
    selftest = "--selftest" in sys.argv

    if selftest:
        return run_selftest()

    # Find repo root (this script is at repo root level)
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent if script_dir.name == "scripts" else script_dir

    logs = find_handoff_logs(repo_root)

    if not logs:
        # No logs yet — valid (pre-seeding)
        return 0

    all_violations: list[str] = []
    exit_code = 0

    for log_path in logs:
        try:
            content = log_path.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"ERROR: cannot read {log_path}: {exc}", file=sys.stderr)
            return 2

        code, violations = validate_log(content, bootstrap=bootstrap, log_path=log_path)
        if code == 2:
            print(f"SCHEMA ERROR in {log_path}:", file=sys.stderr)
            for v in violations:
                print(f"  {v}", file=sys.stderr)
            return 2
        if code == 1:
            exit_code = 1
            for v in violations:
                all_violations.append(f"{log_path}: {v}")

    if all_violations:
        print("HANDOFF_LOG validation failures:", file=sys.stderr)
        for v in all_violations:
            print(f"  {v}", file=sys.stderr)

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
