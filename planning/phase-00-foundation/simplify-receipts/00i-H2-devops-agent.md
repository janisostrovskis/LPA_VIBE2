# Simplify receipt — 00i H2 devops-agent 2026-04-09

## Files reviewed
- `scripts/hooks/pretool_bash_baseline.py` (150 lines)
- `scripts/hooks/posttool_bash_scope_guard.py` (466 lines)
- `.claude/settings.json` (hook registration only)

## Findings (if any)
- `posttool_bash_scope_guard.py` is the larger of the two (466 lines) because the embedded selftest builds a real tempdir git repo to validate checkout/revert behavior. The selftest is ~200 lines of the total; the production hook logic is ~260 lines. This is load-bearing — without a real `git init` in the tempdir, the `git checkout --` revert path would be untested and the hook would silently fail in production.
- The ignore list (IGNORE_PREFIXES / IGNORE_SUFFIXES) is a flat tuple, not a regex — intentionally simple so future additions are just one line each.
- `pretool_bash_baseline.py` is always fail-open (exit 0). This is correct: a failed baseline snapshot must not block the Bash call; worst case it leaves a guard gap, which is better than destroying in-progress work.
- No helper abstractions extracted between the two files — they share `scope_matcher` (from 00h H3) but nothing else, and introducing a third "hook utilities" module for two call sites would be premature.

## Verdict
PASS — clean
