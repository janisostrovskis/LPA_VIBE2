# Simplify Receipt -- 01b H0 -- devops-agent -- 2026-04-09

## Handoff
01b H0 -- devops-agent -- 2026-04-09

## Scope (files modified)

| File | Change |
|------|--------|
| `scripts/hooks/commit_msg_simplify_gate.py` | Added `encoding="utf-8", errors="replace"` to `open()` call reading commit-msg file |
| `scripts/hooks/posttool_bash_scope_guard.py` | Added `encoding="utf-8", errors="replace"` to `open()` call reading tool-input JSON |
| `scripts/hooks/pretool_bash_baseline.py` | Added `encoding="utf-8", errors="replace"` to `open()` call reading stdin payload |
| `scripts/security_scan.py` | Added `encoding="utf-8", errors="replace"` to `open()` call reading scanned files |

Each change is a one-line kwarg addition. No logic was altered.

## Simplify Decision
**waived -- one-line encoding fix + selftest harness per call site, no logic to simplify**

## Rationale
Each change is a minimal `encoding="utf-8", errors="replace"` kwarg addition to an existing
`open()` call. There is no logic to simplify: no branches were added, no abstractions
introduced, no dead code created. The selftest cases added per file are straightforward
harnesses -- a disposable `git init` in a tempdir, a Latvian multi-byte fixture string
written as a commit message or file content, then the hook invoked against it. There is
nothing to collapse or extract. Simplify is waived because the rule targets complexity
reduction, and these diffs have zero complexity delta.

## Selftest Approach
Each selftest isolates from the real repository by:
1. Creating a disposable `git init` in a `tempfile.mkdtemp()` directory.
2. Setting `GIT_INDEX_FILE` and `GIT_DIR` env vars to point at the temp repo so git
   commands cannot touch the real index.
3. Writing a Latvian multi-byte fixture (e.g. "Labdien: pirkt skaistumu") to a temp file
   that mimics the real hook input (commit-msg file, JSON payload, or source file).
4. Invoking the hook function directly and asserting it does not raise `UnicodeDecodeError`.
5. Cleaning up via `shutil.rmtree` in a `finally` block.

## Rule 3 Verification

| Command | Exit code |
|---------|-----------|
| `python scripts/hooks/commit_msg_simplify_gate.py --selftest` | 0 |
| `python scripts/hooks/posttool_bash_scope_guard.py --selftest` | 0 |
| `python scripts/hooks/pretool_bash_baseline.py --selftest` | 0 |
| `python scripts/security_scan.py --selftest` | 0 |
| `pre-commit run --files scripts/hooks/commit_msg_simplify_gate.py scripts/hooks/posttool_bash_scope_guard.py scripts/hooks/pretool_bash_baseline.py scripts/security_scan.py` | 0 |
