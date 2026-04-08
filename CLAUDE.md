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
