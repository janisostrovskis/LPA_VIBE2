# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Latvijas Pilates Asociācija (LPA)** — the national Pilates association website and membership platform for Latvia. This is a greenfield project being built from design documentation.

**Primary goals:** membership management, professional certification/CPD tracking, training registration with payment, instructor/studio directory with "LPA Verified" badge, and multilingual content (LV/EN/RU).

**Key audiences:** Pilates instructors, studio/organization owners, general public, media/partners.

## Design System

The design language is defined in `docs/LPA_DESIGN_LANGUAGE.MD`. Key constraints:

- **Colors:** Neutral-heavy (70-80% white/greys), accents are sage (#9CAF88), mint (#E8F4F0), beige (#E8DCC4), taupe (#C9B8A8). Max 2 accent colors per component.
- **Fonts:** Songer (display headings), Montserrat (UI/body), Winterlady (short accent words only, never in nav/body/forms).
- **Layout:** Max content width 1200-1280px, 12-column grid, 8px spacing scale. Breakpoints: mobile <768, tablet 768-1023, desktop 1024-1439, wide 1440+.
- **Components:** Pill-shaped buttons (border-radius: 9999px), 12px radius cards, one primary button per view. Motion should feel like "breathing" — slow, subtle.
- **Accessibility:** WCAG 2.2 AA compliance required. Min 16px body text, focus states on all interactive elements, `aria-*` attributes on forms.

Use CSS custom properties (`--lpa-*` tokens) or Tailwind mapping from the design doc. Do not introduce ad-hoc hex codes or fonts.

## Business Requirements

Full functional spec is in `docs/LPA_BUSINESS_CASE.MD`. Core modules:

1. **Accounts** — individual + organization, roles (Member, Org admin, Content editor, Reviewer, Site admin)
2. **Memberships & Payments** — auto status lifecycle (Active → Grace → Lapsed), automated reminders
3. **Trainings & Registration** — capacity control, seat confirmation after payment, waitlist
4. **Certification & CPD** — application workflow, public credential verification by certificate ID
5. **Directory** — instructors & studios with LPA Verified badge, application/review/expiry cycle
6. **Events & Ticketing** — optional in MVP
7. **News/Blog** — category-based, multilingual, SEO-friendly
8. **Resources/Downloads** — public + members-only access control
9. **Multilingual** — LV (primary), EN, RU with language-aware URLs, search, and emails
10. **Admin Console** — content + data management, role-based access, activity logs, CSV exports

## Technical Constraints

- Responsive web only (no native mobile app)
- GDPR-compliant: data minimization, export/deletion support, consent tracking
- Payment provider not yet selected — architecture should be provider-agnostic
- External integrations limited to: payments, email, analytics
- **Dual-platform development.** The user develops on **both Windows (Git Bash) and macOS**. Every command, dependency, script, and config any agent writes MUST work on both. Use `pathlib`, forward slashes, POSIX-shell syntax, no PowerShell, no `cmd`, no platform-only binaries without a PEP 508 marker or equivalent gate. Why: Phase 00a shipped a `semgrep` dev dep that broke Windows install — see `planning/phase-00-foundation/RETROSPECTIVE.md` Finding 2.

## Tech Stack

- **Backend:** FastAPI (Python 3.12+) with SQLAlchemy ORM + Alembic migrations + Pydantic validation
- **Frontend:** Next.js (App Router) with TypeScript strict + Tailwind CSS
- **Database:** PostgreSQL
- **Auth:** JWT + magic link (FastAPI backend issues tokens, Next.js frontend consumes them)
- **Payments:** Provider-agnostic (likely Montonio, Kevin., or Klix for Latvian bank links). Abstracted behind `PaymentGateway` port.
- **Testing:** pytest (backend), Vitest (frontend), Playwright (E2E)
- **Dev environment:** Docker Compose (backend + PostgreSQL + frontend)

Two-service monorepo: `backend/` (FastAPI) and `frontend/` (Next.js).

## Architecture Rules (COLA)

This project follows **Clean Object-oriented Layered Architecture (COLA)**. The two-service split physically enforces layer boundaries — the frontend cannot import backend domain code because they are separate services in separate languages.

### Service responsibilities

| Service | Role | Contains |
|---------|------|----------|
| `backend/` (FastAPI) | All business logic, data, integrations | Domain + Application + Infrastructure + API adapter layers |
| `frontend/` (Next.js) | UI rendering, routing, i18n | Adapter layer only — calls backend API, never contains business logic |

### Backend layer locations and import rules

| Layer | Directory | May import from |
|-------|-----------|----------------|
| Domain | `backend/app/domain/` | Nothing outside `backend/app/domain/` and `backend/app/lib/` |
| Application | `backend/app/application/` | `backend/app/domain/`, `backend/app/lib/` |
| API (Adapter) | `backend/app/api/` | `backend/app/application/`, `backend/app/domain/`, `backend/app/lib/` |
| Infrastructure | `backend/app/infrastructure/` | `backend/app/application/ports/`, `backend/app/domain/`, `backend/app/lib/` |

**Violations are build errors.** The pre-commit hook `scripts/check_cola_imports.py` rejects commits that break these rules. If you need something from a forbidden layer, you are structuring the code wrong — refactor, do not bypass.

### Key constraints

- The Domain layer is **pure Python**. No FastAPI, SQLAlchemy, Pydantic BaseModel (use dataclasses), or any framework imports.
- The Application layer defines **ports** (Python ABCs in `application/ports/`). Infrastructure provides concrete implementations.
- The Frontend never contains business logic. All data flows through the backend API. The frontend's `lib/api-client.ts` is the single point of contact.
- No file (`.py`, `.ts`, `.tsx`) may exceed **2,000 lines**. Pre-commit hook enforces this. At **1,500 lines**, split proactively.

## Development Process

### Strict rules for all development work

Full process details are in `docs/DEVELOPMENT_RULEBOOK.MD`. These are the non-negotiable rules:

### Before writing code

1. Check that a plan exists in `planning/` for the current phase.
2. If no plan exists, create one following the template in `docs/DEVELOPMENT_RULEBOOK.MD` section B.8.
3. Identify which agent scope this work falls under. Never modify files outside your scope.

### Agent scope boundaries

| Agent | Owns (read/write) | Cannot touch |
|-------|-------------------|-------------|
| Database Agent | `backend/app/infrastructure/database/`, `backend/app/domain/entities/`, `backend/app/domain/value_objects/`, `alembic/` | Frontend, payment adapters |
| Backend Agent | `backend/app/application/`, `backend/app/domain/rules/`, `backend/app/domain/events/`, `backend/app/domain/errors/` | Frontend, infrastructure concrete |
| Frontend Agent | `frontend/src/` (all) | Backend (all) |
| Payments Agent | `backend/app/infrastructure/payments/`, `backend/app/application/ports/payment_gateway.py` | Everything else |
| Security Agent | Read-only audit of everything. Owns `backend/app/api/middleware/`, `backend/app/infrastructure/config/`, `.gitignore`, `scripts/` | Files issues for other agents to fix |
| i18n Agent | `frontend/public/locales/`, translation-related components | Domain, application, infrastructure |
| DevOps Agent | Root configs, `scripts/`, CI/CD, Docker files | Application code |
| Efficiency Agent | `.claude/agents/*.md`, `CLAUDE.md`, `docs/DEVELOPMENT_RULEBOOK.MD`, `planning/**/RETROSPECTIVE.md` (process docs only) | All code, tests, infrastructure, `.claude/settings.json` |

### Runtime enforcement

The scope table above is enforced at runtime by `scripts/hooks/pretool_scope_guard.py`, which reads `.claude/scope.yaml` (the machine-readable source of truth) and blocks `Write`/`Edit` calls outside the caller's allow list. Main session is restricted to `planning/**`, `CLAUDE.md`, `.claude/**`, `docs/**`. If you genuinely need to edit an out-of-scope file (emergency unblock only), write a justification to `.claude/scope-override`: the next edit consumes the file, logs the reason to `.claude/scope-override-audit.log` (git-tracked), and proceeds. More than one override per sub-phase is a retrospective finding.

Every handoff must be recorded in `planning/phase-NN/HANDOFF_LOG.md` with the schema documented there. `scripts/check_handoff_log.py` validates the log in pre-commit and in the CI `handoff-hygiene` job — a missing or malformed entry blocks the merge.

Every sub-phase commit that touches `backend/app/**` or `frontend/src/**` must carry a `Simplify:` decision in the commit body: `Simplify: ran, clean` / `Simplify: ran, <N> findings addressed ...` / `Simplify: waived — <reason>`. The `scripts/hooks/commit_msg_simplify_gate.py` commit-msg hook rejects commits that don't. `git commit --no-verify` is denied by `.claude/settings.json` — do not attempt to bypass.

### While writing code

- **Fail loudly.** Never swallow errors. No bare `except:` or `except Exception: pass` in Python. No empty catch blocks in TypeScript. No unhandled promise rejections. If something fails, surface it. The only exception: items documented with `# FAIL-QUIET-EXCEPTION:` comment, including rationale, logged at WARNING level minimum, and approved in the phase plan document.
- **No hardcoded secrets.** All credentials come from environment variables loaded through `backend/app/infrastructure/config/env.py` (Pydantic Settings). The env loader validates at startup and refuses to start on missing values.
- **No ad-hoc styles.** Use `--lpa-*` design tokens or their Tailwind equivalents only. No hex codes outside the design system.
- **Strict typing.** Python: type hints on all functions + mypy strict. TypeScript: strict mode, no `any` except with a justifying comment, no `@ts-ignore` without a linked issue.

### After completing a phase

1. Run `/simplify` on all changed files. Fix all findings. Repeat until clean.
2. Complete the security review checklist in `planning/phase-NN/SECURITY_REVIEW.md`.
3. Complete the testing gate in `planning/phase-NN/TESTING_GATE.md`.
4. Invoke the **Efficiency Agent** to retrospect on the phase. Apply any process amendments it produces.
5. **All four must pass before starting the next phase.** No exceptions.

### Subagent dispatch preamble

Every execution brief sent to a shipping agent (frontend, backend, database, payments, devops, security, i18n) MUST begin with the following sentence verbatim, on its own line, in bold:

> **Execute the following. This is not a planning task. Do not enter plan mode. Do not present a plan back to the orchestrator. Write files directly. If the brief is ambiguous, ask one focused clarifying question — do not write a plan file.**

The preamble exists because subagents repeatedly entered plan mode in Phase 0 sub-phases 00e and 00f, costing dispatch roundtrips. The exact sentence is matchable by future enforcement tooling. Briefs that omit it are presumed defective.

### Parallel dispatch for independent handoffs

When a plan contains two or more handoffs with **no file overlap and no ordering dependency**, main session MUST dispatch them as multiple `Agent` tool calls in a **single message**. Serializing independent handoffs wastes one full dispatch roundtrip (~several minutes) per parallelizable pair.

Worked example — 00h H1 and H3 were independent (H1 edited `scripts/check_handoff_log.py` + 7 agent `.md` files under devops scope; H3 edited `scripts/preflight_dispatch.py` + `scripts/hooks/scope_matcher.py` under devops scope; no file overlap). They shipped sequentially and cost ~5 minutes of wasted wall-clock. The correct pattern would have been one message containing two `Agent(subagent_type="devops-agent", ...)` calls.

Pre-flight protocol for parallel dispatch:
1. For each handoff, run `python scripts/preflight_dispatch.py --agent <name> --files <list>`. All must exit 0.
2. Verify the union of all handoff file sets has no duplicates — any duplicate file is a dependency and forces sequential ordering.
3. Dispatch all `Agent` calls in one message.
4. After both return, stage, commit, and push as separate commits in dependency order (usually doesn't matter since they don't overlap).

The Agent tool handles concurrent subagents natively — no extra configuration is needed.

### CI watch — background by default

After every `git push`, main session MUST invoke `gh run watch <id> --exit-status` via the Bash tool's `run_in_background: true` parameter, **not** block on it. Main session continues with the next handoff's planning and dispatch while CI runs in parallel. The only *blocking* `gh run watch` is at **sub-phase close**, when all handoffs have landed and the gate check needs every run green before moving to the retrospective.

This trades atomic revert granularity (you discover a red CI one or two handoffs later) for ~2 minutes saved per handoff inside a sub-phase. The trade-off is acceptable because:
- Pre-commit locally catches the common failures before they reach CI.
- Main-branch protection still requires green CI before any merge.
- A red CI reverts one commit, not a whole sub-phase.
- Sub-phase close runs a final blocking watch across all commits, so nothing ships without full green.

When a background watch reports failure (the task-notification surfaces after completion), main session must immediately investigate and either roll forward with a fix commit or revert the broken commit, before continuing with the next handoff.

### Known limitation — new subagent registration

Claude Code discovers `.claude/agents/*.md` at **session start**. A new agent file created mid-session is not picked up until the session restarts. If you just created a new agent and `subagent_type` does not list it, invoke it via `general-purpose` for the rest of the current session and it will be directly invokable next session. This is not a bug in the agent file — no amendment to the frontmatter will fix it.

### When to invoke the Efficiency Agent (mid-cycle)

Outside of phase boundaries, invoke Efficiency Agent when any of these occur:

- A tool or command failed 2+ times in the same session (signal: workflow gap, not transient error)
- An agent did work that should have been handed off to another agent (signal: scope confusion in agent docs)
- The user had to correct the assistant's approach after work was already produced (signal: missing upfront rule)
- A platform-specific command broke on Windows or macOS (signal: cross-platform regression)
- A hallucinated file/skill/command was referenced (signal: missing verification rule)

The Efficiency Agent is **not** invoked for one-off mistakes or transient failures. Its job is to detect *patterns* and amend process docs.

## Fail-Loudly Principle

**Default rule:** Every error must surface to the nearest responsible party. Silent failure is a bug.

- **Python:** No bare `except:`. No `except Exception: pass`. Ruff rule `E722` (bare-except) and custom lint for `pass`-only handlers enforced.
- **TypeScript:** No empty catch blocks. ESLint `no-empty` with `allowEmptyCatch: false`. `@typescript-eslint/no-floating-promises` set to `error`.
- **Result type:** Use cases return `Result[T, DomainError]` (from `backend/app/lib/result.py`) instead of raising exceptions for expected failures. The API layer inspects the result and returns appropriate HTTP status codes.
- **Env validation:** `backend/app/infrastructure/config/env.py` uses Pydantic Settings to parse environment variables. Missing or malformed required variables cause the application to refuse to start with a clear error naming the missing variable.
- **Payments are never fire-and-forget.** Every payment call must await confirmation and handle all failure modes explicitly. A payment failure must result in a visible status change — enrollment stays `PENDING`, membership is not activated.
- **Exception process:** If a specific case genuinely warrants a silent fallback (e.g., analytics failure must not block user action):
  1. Document with `# FAIL-QUIET-EXCEPTION:` comment including rationale
  2. Log the error at WARNING level minimum
  3. Get approval noted in the phase plan document
  4. Security agent reviews during phase review

## Multilingual Content

- **LV is the primary language.** All UI strings must exist in LV first.
- Translation files live in `frontend/public/locales/{lv,en,ru}/`.
- URLs use `[locale]` prefix: `/lv/apmacibas`, `/en/trainings`, `/ru/treningi`.
- Backend emails respect the user's `preferred_language` field.
- If a translation is missing, fall back to LV. Never show a blank string or raw translation key to the user.

## Payment Integration

- Payment provider is abstracted behind `backend/app/application/ports/payment_gateway.py` (Python ABC).
- Never import any payment provider SDK outside `backend/app/infrastructure/payments/`.
- Payment webhooks must verify signatures before processing any data.
- No seat confirmation without confirmed payment. Enrollment status stays `PENDING` until the payment webhook confirms success.

## Error Handling Patterns

- **Domain errors:** Raise typed errors from `backend/app/domain/errors/`.
- **Use case results:** Return `Result[T, E]` from `backend/app/lib/result.py`.
- **API routes:** Catch errors and return structured JSON with appropriate HTTP status codes. Never expose stack traces in API responses.
- **Frontend:** Display error messages from the backend API. Never show raw stack traces to users.
- **Logging:** Use `backend/app/lib/logger.py` (structured logging). Never `print()` or `console.log()` in production code.
