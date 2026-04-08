# Phase 00: Foundation

## Objective

Establish a guardrail-only bootstrap for the LPA platform: build tooling, CI skeleton, COLA import enforcement, file-size enforcement, and secret scanning. No application code is written in this phase. The deliverables exist purely so that all subsequent phases land in a structured environment where bad commits are rejected at the door.

This phase is split into six sub-phases (00a–00f). Sub-phase **00a** is being executed now and is the subject of this plan. Sub-phases 00b–00f are stubbed in the Sub-phases section below and will be planned individually as they are taken up.

## Prerequisites

- `CLAUDE.md`, `docs/DEVELOPMENT_RULEBOOK.MD`, `docs/LPA_BUSINESS_CASE.MD`, `docs/LPA_DESIGN_LANGUAGE.MD`, `planning/MASTER_PLAN.md` all present and committed.
- Agent definitions for `database-agent`, `backend-agent`, `frontend-agent`, `payments-agent`, `devops-agent`, `security-agent`, `i18n-agent`, `efficiency-agent` present in `.claude/agents/`.
- `.claude/settings.json` permission allow-list already permits `python scripts/check_file_size.py*`, `python scripts/check_cola_imports.py*`, and `python scripts/security_scan.py*`.
- No prior phase gate (this is the first phase).

## Deliverables

Sub-phase 00a delivers the following six files. The remaining nine items from `planning/MASTER_PLAN.md` Phase 0 (lines 245-260) are deferred to sub-phases 00b–00f.

1. `planning/phase-00-foundation/PLAN.md` — this document
2. `backend/pyproject.toml` — Python project metadata, runtime + dev dependencies, and tool configuration (`[tool.ruff]`, `[tool.mypy]`, `[tool.bandit]`, `[tool.pytest.ini_options]`)
3. `.github/workflows/ci.yml` — GitHub Actions workflow with the eight-stage pipeline defined in `.claude/agents/devops-agent.md` lines 63-71. Frontend-related stages and the integration-tests job are gated with `hashFiles()` so they no-op on the empty repo
4. `scripts/check_file_size.py` — rejects any `.py`, `.ts`, or `.tsx` file in `backend/` or `frontend/` exceeding 2000 lines, warns at 1500. Supports `--selftest`
5. `scripts/check_cola_imports.py` — enforces COLA import rules from `CLAUDE.md` lines 71-78 against `backend/app/`. AST-based, stdlib only. Supports `--selftest`. No-op on the empty repo
6. `scripts/security_scan.py` — high-confidence regex scan over tracked files for AWS/Stripe/GitHub tokens, private keys, generic password assignments, JWT secrets, and hardcoded DB URLs. Supports `--selftest`

## Sub-phases

| Sub-phase | Scope | Status |
|-----------|-------|--------|
| **00a** | Backend toolchain (`pyproject.toml`) + CI (`ci.yml`) + 3 enforcement scripts | Complete |
| **00b** | `docker-compose.yml` + `backend/Dockerfile` + `.dockerignore`s + `.env.example` + first push (frontend Dockerfile deferred to 00c) | **In progress** |
| 00c | `frontend/package.json`, `tsconfig.json`, `vitest.config.ts`, `playwright.config.ts`, ESLint config (`no-empty`, `no-floating-promises`) | Not started |
| 00d | `backend/app/lib/result.py`, `backend/app/lib/errors.py`, `backend/app/lib/logger.py` | Not started |
| 00e | `backend/app/infrastructure/config/env.py` (Pydantic Settings, fail-loudly validation) | Not started |
| 00f | Full empty folder tree with `__init__.py` files matching the COLA layer layout | Not started |

The Phase 0 testing gate from `planning/MASTER_PLAN.md` line 262 ("Both services start via Docker Compose. Pre-commit hooks reject a deliberately oversized file AND a deliberately wrong-layer import. CI pipeline passes on a clean commit.") cannot fully PASS until 00b–00f complete. 00a delivers the *halves* of those checks that are local-only (script self-tests). The Docker Compose half lands in 00b.

## Agent Assignments

| Deliverable | Owner | Rationale |
|-------------|-------|-----------|
| 1. `planning/phase-00-foundation/PLAN.md` | Main session | DevOps Agent is forbidden from `planning/` per `.claude/agents/devops-agent.md` line 37 |
| 2. `backend/pyproject.toml` | DevOps Agent | Explicit ownership in `.claude/agents/devops-agent.md` line 19 |
| 3. `.github/workflows/ci.yml` | DevOps Agent | "CI/CD configuration files (GitHub Actions, etc.)" line 28 |
| 4. `scripts/check_file_size.py` | DevOps Agent | "All enforcement scripts" line 25 |
| 5. `scripts/check_cola_imports.py` | DevOps Agent | Same |
| 6. `scripts/security_scan.py` | DevOps Agent | Same |

## Handoffs

Within sub-phase 00a:

- **HANDOFF: Main Session → DevOps Agent**: Create deliverables 2-6 per the constraints listed in the "Risks and Mitigations" section below. Acknowledge with "HANDOFF ACK" and report back with "HANDOFF COMPLETE: 00a — PASS" plus the verification output.

Pre-identified handoffs for future sub-phases (not actioned now, recorded so they are not forgotten):

- 00d: HANDOFF: DevOps → Backend Agent — `backend/app/lib/` is `backend/app/` and therefore Backend Agent scope, not DevOps. DevOps creates the test fixtures and config; Backend writes the actual `result.py`, `errors.py`, `logger.py`.
- 00e: HANDOFF: DevOps → Backend Agent — `backend/app/infrastructure/config/env.py` is application code and belongs to Backend Agent scope per the same rule.

## Testing Requirements

These tests must all pass before sub-phase 00a is declared complete. They are run by the main session after the DevOps Agent reports HANDOFF COMPLETE.

1. **Toolchain installs cleanly:** `cd backend && python -m pip install -e .[dev]` exits 0. All dev tools (`ruff`, `mypy`, `bandit`, `semgrep`, `pip-audit`) become importable / runnable.
2. **Ruff baseline passes:** `cd backend && ruff check .` exits 0 on the empty package.
3. **`check_file_size.py` clean run:** `python scripts/check_file_size.py` exits 0 on the clean repo.
4. **`check_file_size.py` self-test:** `python scripts/check_file_size.py --selftest` exits 1 with the synthetic 2001-line file named.
5. **`check_cola_imports.py` clean run:** `python scripts/check_cola_imports.py` exits 0 on the clean repo (no `backend/app/` exists yet — the script must handle this gracefully).
6. **`check_cola_imports.py` self-test:** `python scripts/check_cola_imports.py --selftest` exits 1 with a synthetic `backend/app/domain/x.py` containing `from fastapi import FastAPI` flagged. **This is the only end-to-end validation possible without real backend code on disk.**
7. **`security_scan.py` clean run:** `python scripts/security_scan.py` exits 0 on the clean repo.
8. **`security_scan.py` self-test:** `python scripts/security_scan.py --selftest` exits 1 with a synthetic file containing `AKIAIOSFODNN7EXAMPLE` flagged.
9. **CI workflow YAML lints clean:** `pipx run yamllint .github/workflows/ci.yml` exits 0.
10. **Cross-platform sanity:** Steps 1-9 run inside Git Bash on Windows (this machine). macOS validation is the user's responsibility on the other machine; scripts use only `pathlib`, `subprocess`, `re`, and `argparse` so should be platform-clean by construction.

The standard Phase 0 gate items (Docker Compose, "deliberately oversized file" rejected end-to-end, CI passing on a clean commit) are deferred to sub-phases 00b and beyond. Documenting the deferral here so it is not silently dropped.

## Acceptance Criteria

`planning/MASTER_PLAN.md` line 264 explicitly states: **"Acceptance criteria ref: N/A (infrastructure phase)"**. Phase 0 has no business-case acceptance criteria; the testing gate is its only success measure.

## Risks and Mitigations

| # | Risk | Mitigation |
|---|------|------------|
| R1 | Ruff has no built-in lint for "`pass`-only exception handler". `CLAUDE.md` line 144 mentions a "custom lint" but no such tool exists yet. | Use ruff `S110` (try-except-pass) and `BLE001` (blind-except) together as a proxy. Document this gap explicitly. A true bespoke AST check is deferred to sub-phase 00d. |
| R2 | The repo has no `origin` remote. `.github/workflows/ci.yml` cannot run end-to-end until pushed. | Validate locally with `pipx run yamllint`. Defer first push (and first real CI run) to sub-phase 00b, when `docker-compose.yml` and the initial repo publish land together. |
| R3 | `mypy --strict` against an empty `backend/app/` package errors with "no modules to check". | Gate the `typecheck` job in CI with `if: hashFiles('backend/app/**/*.py') != ''`. The job is therefore skipped on the empty repo and activates automatically once any `.py` lands in `backend/app/`. |
| R4 | The PostgreSQL service in the `integration-tests` CI job spins up wastefully when no integration tests exist. | Gate the entire job with `if: hashFiles('backend/tests/integration/**')`. |
| R5 | Phase 0 testing gate (per `MASTER_PLAN.md` line 262) cannot fully PASS until sub-phases 00b–00f land. | Sub-phase ordering documented above. The full Phase 0 `TESTING_GATE.md` and `SECURITY_REVIEW.md` are deferred to 00f, when all Phase 0 deliverables exist. |
| R6 | `semgrep --config auto` requires network access at scan time and is non-reproducible across runs. | Pin to `--config p/python --config p/security-audit` in CI. No `--config auto`. |
| R7 | Cross-platform breakage: Windows + macOS dual-development means a script using PowerShell-only or backslash paths breaks half the team. | Hard rule: all scripts use `pathlib.Path`, no shell calls except `subprocess` with cross-platform args, no PowerShell, no backslashes. Verification step 10 enforces by running on Windows under Git Bash. |
| R8 | The `/simplify` post-phase step from `CLAUDE.md` "After completing a phase" expects code files, but 00a produces only infrastructure (TOML, YAML, Python scripts that are tooling, not application code). | Document that `/simplify` is N/A for 00a. The Efficiency Agent retrospective is still run, replacing the missing `/simplify` step as the post-phase quality check for this sub-phase. |
| R9 | Hardcoding `pydantic.BaseModel` ban via AST `ImportFrom` misses `import pydantic; pydantic.BaseModel.X`. | Accept the limitation. The check still catches the dominant idiom (`from pydantic import BaseModel`). A complete solution would require `Attribute` node analysis and is deferred. Documented in the script header. |
| R10 | DevOps Agent might inadvertently touch `.claude/settings.json` or `planning/`. | Both are explicitly forbidden in the handoff message and reinforced by the agent's own `MUST NOT touch` list. Verification step 10 confirms by inspecting the diff before declaring complete. |
| R11 | Frontend Dockerfile deferred to 00c despite the original 00b row mentioning it. | `frontend/package.json` does not exist yet (it lands in 00c), so a frontend Dockerfile would have nothing to COPY. The compose file reserves the slot as a TODO comment so `docker compose config` parses cleanly. |
| R12 | Backend container `CMD` is a placeholder; `docker compose up backend` will exit immediately. | `app/main.py` does not exist yet (lands in 00f). CMD prints a clear stderr message and exits 0. `restart: "no"` prevents looping. Real uvicorn CMD lands in 00f. |
| R13 | `gh` CLI on this machine is authed under `Android2488`, but target account is `janisostrovskis`. `gh repo create` cannot be used from this machine. | User creates the empty `janisostrovskis/LPA_VIBE2` repo via the GitHub web UI before the push step. Main session updates the `origin` URL via `git remote set-url` and pushes. |
| R14 | `setuptools.packages.find` with no matching `app/` dir may emit a warning during `pip install -e .` inside the slim image. | Already verified on host (00a Step 1). If the slim image behaves differently, add `RUN pip install -U setuptools` before `pip install -e .` in the Dockerfile. Apply only if Step 2 fails. |
| R15 | Bind mount `./backend:/app` shadows the `.egg-info` produced by `pip install -e .`, breaking imports inside the long-running container. | Verification uses `docker compose run --rm` (which still mounts the volume). If imports fail inside the container, switch to a named volume for `/app/lpa_backend.egg-info` or COPY the metadata explicitly. Revisit in Phase 1 if it bites. |
| R16 | `.venv-bootstrap-check/` from 00a verification is in the working tree but not matched by the existing `.gitignore` `.venv/` pattern. | DevOps Agent updates `.gitignore` to use `.venv*/` so any future bootstrap venv is excluded. The explicit `git add` list at push time also excludes it as a belt-and-braces measure. |
| R17 | DevOps Agent wrote `DATABASE_URL=postgresql+psycopg://...` in both `docker-compose.yml` and `.env.example`. The `+psycopg` form is a SQLAlchemy URL convention; raw psycopg3 / libpq / the MCP postgres server cannot parse it. Caught by 00b verification Step 5 (`psycopg.connect(url)` raised `ProgrammingError`). | Main session edited `docker-compose.yml` to use the libpq-compatible `postgresql://lpa:lpa@db:5432/lpa` and added a comment. `.env.example` requires the same edit but is denied by the main session's permission settings — the user must apply the one-line change manually before sub-phase 00e (env loader) lands. The env loader in 00e will be responsible for deriving the SQLAlchemy `postgresql+psycopg://` form from the libpq DATABASE_URL. This is a systemic agent failure (devops-agent generated a URL scheme without verifying it parses with the actual driver) — a follow-up retrospective amendment to `devops-agent.md` may be warranted; deferred to the next efficiency-agent invocation. |

## Sub-phase 00b deliverables

DevOps Agent owns these five files:

1. `docker-compose.yml` (root) — `db` (postgres:16-alpine, healthcheck via `pg_isready`) + `backend` (build from `./backend`, `depends_on: db: service_healthy`). Frontend service is a TODO comment for 00c.
2. `backend/Dockerfile` — `python:3.12-slim`, `pip install -e .` (NOT `[dev]`), placeholder `CMD` exits 0 with stderr message.
3. `backend/.dockerignore` — exclude caches, venvs, `.env*` (keep `.env.example`), `.git/`.
4. `.dockerignore` (root) — equivalent for root-context builds.
5. `.env.example` (root) — POSTGRES_*, DATABASE_URL (psycopg3 scheme), BACKEND_PORT, commented placeholders for auth/payments/frontend with `# pragma: allowlist secret` on the JWT example.

Plus a small .gitignore amendment (DevOps scope, root config): broaden `.venv/` to `.venv*/` so `.venv-bootstrap-check/` is excluded (R16).

Main session steps after handoff:

6. Run the verification suite (see Testing Requirements 11–18 below).
7. Pause and ask user to create empty `https://github.com/janisostrovskis/LPA_VIBE2` repo via GitHub web UI.
8. `git remote set-url origin https://github.com/janisostrovskis/LPA_VIBE2.git`, explicit `git add` list, `git status` review pause, then user-approved `git commit` + `git push -u origin master`.

## Handoffs (00b)

- **HANDOFF: Main Session → DevOps Agent**: Create deliverables 1–5 above plus the `.gitignore` amendment. Constraints: cross-platform Docker Desktop (Windows + macOS), `docker compose` v2 syntax, no frontend Dockerfile, no real uvicorn CMD, must not touch `planning/` or `.claude/settings.json` or 00a deliverables. Acknowledge with "HANDOFF ACK" and report back with "HANDOFF COMPLETE: 00b — files created" plus the file list.

## Testing Requirements (00b additions)

11. **Compose config parses:** `docker compose config > /dev/null` exits 0.
12. **Backend image builds:** `docker compose build backend` exits 0.
13. **Postgres comes up healthy:** `docker compose up -d db` then poll `docker inspect --format='{{.State.Health.Status}}' lpa-db` until `healthy` (max 30s).
14. **Backend deps importable:** `docker compose run --rm backend python -c "import fastapi, sqlalchemy, alembic, pydantic, pydantic_settings, psycopg; print('ok')"` exits 0.
15. **Backend reaches db:** `docker compose run --rm backend python -c "import psycopg, os; conn=psycopg.connect(os.environ['DATABASE_URL']); cur=conn.cursor(); cur.execute('SELECT 1'); print(cur.fetchone())"` prints `(1,)`.
16. **Backend CMD behaves as documented:** `docker compose run --rm backend` prints the placeholder stderr message and exits 0.
17. **Cleanup:** `docker compose down -v` exits 0; `lpa-db-data` volume removed.
18. **Security scan covers `.env.example`:** `python scripts/security_scan.py` exits 0 with the new file in the tracked set.
