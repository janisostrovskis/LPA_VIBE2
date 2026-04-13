# Phase 02 — Accounts & Authentication

## Context

Phase 01 (Design System) is complete with all gates passed. Phase 02 is the
mandatory foundation for all subsequent phases — every feature (memberships,
trainings, certification, directory, payments) depends on user accounts and
authentication being in place.

Per `planning/MASTER_PLAN.md` Phase 2 definition (lines 287-303):

> Users and organizations can register, log in, manage profiles. Role system
> enforced. Admin route protection in place.

Backend scaffolding exists (COLA directories, `result.py`, `errors.py`,
`env.py`, `logger.py`) but has zero feature code. This is the first phase
to write Python backend code — COLA import checks will be active for the
first time.

## Scope (from Master Plan + Business Case Section 3.1)

**Must deliver:**

1. Database schema — User, Organization, Role, MagicLinkToken tables
2. Domain entities — Member, Organization; value objects Email, Locale, Role
3. Auth infrastructure — JWT token issuance/validation, magic link flow, password hashing
4. Use cases — register, login (password + magic link), update profile, create org, invite team member
5. API routes — `/api/auth/*`, `/api/members/*`, `/api/organizations/*`
6. Middleware — JWT validation, role-based access control
7. Frontend — registration form, login page, profile editor, org dashboard
8. GDPR — data export endpoint (`GET /api/members/me/export`)

**Not in scope (deferred to later phases):**

- Membership types and payments (Phase 3)
- Training registration (Phase 4)
- Certification (Phase 5)
- Directory profiles (Phase 6)
- Email sending infrastructure (Phase 9 — stub the port in Phase 2)

## Sub-phases

| Sub-phase | Goal                                                                         | Owner(s)                                                  | Parallel?               |
| --------- | ---------------------------------------------------------------------------- | --------------------------------------------------------- | ----------------------- |
| **02a**   | DB schema + Alembic migration (User, Org, Role, MagicLinkToken)              | database-agent                                            | No                      |
| **02b**   | Domain entities + value objects + rules                                      | backend-agent                                             | No (needs 02a entities) |
| **02c**   | Infrastructure: repositories, JWT factory, password hashing, email port stub | database-agent (repos) ‖ backend-agent (JWT + email port) | Yes                     |
| **02d**   | Application use cases: register, login, profile, org management              | backend-agent                                             | No (needs 02c)          |
| **02e**   | API routes + middleware (auth, CORS, RBAC)                                   | backend-agent                                             | No (needs 02d)          |
| **02f**   | Frontend: auth pages, profile, org dashboard, API client                     | frontend-agent                                            | No (needs 02e API)      |
| **02g**   | Integration tests + E2E + close gates                                        | All agents                                                | No                      |

## Sub-phase 02a: Database schema + Alembic migration

**Owner:** database-agent (single handoff H1)

**Deliverables:**

- `backend/app/domain/entities/member.py` — Python dataclass: id (UUID), email, display_name, preferred_locale, password_hash (optional — magic link users have none), is_active, created_at, updated_at
- `backend/app/domain/entities/organization.py` — dataclass: id, legal_name, registration_number, vat_number (optional), address, contact_email, contact_person_name, created_at, updated_at
- `backend/app/domain/value_objects/email.py` — immutable validated Email VO (regex + lowercase normalization)
- `backend/app/domain/value_objects/locale.py` — `Locale` enum: LV, EN, RU
- `backend/app/infrastructure/database/models.py` — SQLAlchemy mapped classes: `UserModel`, `OrganizationModel`, `RoleModel` (join table: user_id, role_name), `MagicLinkTokenModel` (token, user_id, expires_at, used)
- `backend/app/infrastructure/database/session.py` — async SQLAlchemy session factory using `env.py` DATABASE_URL
- `alembic/versions/0001_initial_accounts.py` — initial migration creating the 4 tables
- `backend/tests/domain/test_email_vo.py` — unit tests for Email validation
- `backend/tests/domain/test_locale_vo.py` — unit tests for Locale enum

**Key constraints:**

- Domain entities are **pure Python dataclasses** — no SQLAlchemy, no Pydantic BaseModel
- Infrastructure models use SQLAlchemy ORM Mapped[] syntax
- Roles are string-based: "member", "org_admin", "content_editor", "reviewer", "site_admin"
- UUIDs for all primary keys (use `uuid7` for time-ordering if available, else `uuid4`)
- All timestamps UTC
- Email column: unique, indexed, case-insensitive (use CITEXT or lower() functional index)

**Verification:**

- `(cd backend && python -m pytest tests/domain/)` → 0
- `(cd backend && docker compose up -d db && alembic upgrade head)` → 0
- `(cd backend && python -m mypy app/)` → 0
- `pre-commit run --files <changed>` → 0

## Sub-phase 02b: Domain layer (rules, errors, events)

**Owner:** backend-agent (single handoff H1)

**Deliverables:**

- `backend/app/domain/rules/auth_rules.py` — password strength validation, magic link expiry check
- `backend/app/domain/errors/auth_error.py` — InvalidCredentials, EmailAlreadyRegistered, MagicLinkExpired, InsufficientRole
- `backend/app/domain/events/member_registered.py` — MemberRegistered domain event
- `backend/app/domain/events/member_logged_in.py` — MemberLoggedIn domain event
- Unit tests for all rules and errors

## Sub-phase 02c: Infrastructure (parallel)

**H1 — database-agent:** Repositories

- `backend/app/infrastructure/database/repositories/member_repository.py` — CRUD + find_by_email
- `backend/app/infrastructure/database/repositories/organization_repository.py` — CRUD
- `backend/app/infrastructure/database/repositories/magic_link_repository.py` — create, consume, cleanup_expired
- `backend/app/application/ports/member_repository.py` — ABC port
- `backend/app/application/ports/organization_repository.py` — ABC port
- `backend/app/application/ports/magic_link_repository.py` — ABC port
- Integration tests hitting real test PostgreSQL

**H2 — backend-agent:** Auth infrastructure

- `backend/app/infrastructure/auth/jwt_service.py` — issue + validate JWT (HS256, configurable expiry)
- `backend/app/infrastructure/auth/password_service.py` — bcrypt hash + verify
- `backend/app/application/ports/auth_service.py` — ABC port for JWT
- `backend/app/application/ports/email_sender.py` — ABC port (stub implementation that logs to console)
- Unit tests

## Sub-phase 02d: Application use cases

**Owner:** backend-agent

**Deliverables:**

- `backend/app/application/use_cases/auth/register.py` — RegisterMember use case returning `Result[MemberDto, DomainError]`
- `backend/app/application/use_cases/auth/login_password.py` — password login returning JWT
- `backend/app/application/use_cases/auth/login_magic_link.py` — request + consume magic link
- `backend/app/application/use_cases/auth/refresh_token.py` — JWT refresh
- `backend/app/application/use_cases/member/update_profile.py` — profile edits
- `backend/app/application/use_cases/member/export_data.py` — GDPR export
- `backend/app/application/use_cases/organization/create_organization.py`
- `backend/app/application/use_cases/organization/invite_member.py`
- `backend/app/application/dto/member_dto.py` — Pydantic model for API responses
- `backend/app/application/dto/auth_dto.py` — login request/response schemas
- Unit tests with mocked ports

## Sub-phase 02e: API routes + middleware

**Owner:** backend-agent

**Deliverables:**

- `backend/app/api/routes/auth.py` — POST /register, POST /login, POST /magic-link/request, POST /magic-link/verify, POST /refresh
- `backend/app/api/routes/members.py` — GET /me, PATCH /me, GET /me/export, GET /{id} (admin)
- `backend/app/api/routes/organizations.py` — POST /, GET /{id}, PATCH /{id}, POST /{id}/invite
- `backend/app/api/middleware/auth.py` — JWT validation dependency
- `backend/app/api/middleware/cors.py` — CORS config
- `backend/app/api/dependencies.py` — DI wiring (repository + service instances)
- `backend/app/main.py` — FastAPI app with routers mounted
- Integration tests against running backend

## Sub-phase 02f: Frontend auth pages

**Owner:** frontend-agent

**Deliverables:**

- `frontend/src/lib/api-client.ts` — typed fetch wrapper for backend API
- `frontend/src/app/[locale]/(public)/join/page.tsx` — upgrade from placeholder to registration form
- `frontend/src/app/[locale]/(public)/login/page.tsx` — email + password login, magic link option
- `frontend/src/app/[locale]/(auth)/profile/page.tsx` — profile editor (behind auth)
- `frontend/src/app/[locale]/(auth)/layout.tsx` — auth-required layout (redirects to login if no JWT)
- `frontend/public/locales/{lv,en,ru}/common.json` — auth-related translation keys
- Vitest + Playwright tests

## Sub-phase 02g: Integration + close gates

- Full E2E test: register → login → view profile → update profile → export data
- Docker Compose integration test (backend + frontend + DB)
- Security review (auth is security-critical)
- Testing gate
- Efficiency retrospective

## Process rules (carried from Phase 01)

- Bash cwd discipline: always `(cd foo && cmd)` subshells
- Lockfile regen: always via `docker run node:20-alpine npm install`
- Scope overrides: logged to `.claude/scope-override-audit.log`
- Each handoff: mandatory preamble, Rule 1 (frontend-design for frontend), Rule 2 (simplify), Rule 3 (verification)
- Handoff timing instrumentation via `scripts/log_handoff_timing.py`
- COLA import check will be ACTIVE for the first time (Python files in commits)
- Domain layer: pure Python dataclasses only, no framework imports

## Risks

| #   | Risk                                                                     | Mitigation                                                                  |
| --- | ------------------------------------------------------------------------ | --------------------------------------------------------------------------- |
| R1  | First backend code — COLA import check may surface unexpected violations | database-agent and backend-agent briefs include explicit layer import rules |
| R2  | Async SQLAlchemy + Alembic setup is nontrivial                           | database-agent creates session.py with proven async pattern                 |
| R3  | JWT + magic link auth flow is security-critical                          | Security-agent review at 02g, not just phase close                          |
| R4  | Docker Compose needs to be running for integration tests                 | CI already has service containers; local devs use docker compose            |
| R5  | Frontend API client needs backend running                                | 02f tests can mock API; E2E in 02g tests against real backend               |

## Verification (end of Phase 02)

- `(cd backend && python -m pytest)` → all tests pass
- `(cd backend && python -m mypy app/ --strict)` → 0
- `(cd backend && ruff check app/)` → 0
- `docker compose up -d && curl http://localhost:8000/docs` → Swagger UI loads
- Full registration + login + profile E2E flow via Playwright
- `(cd frontend && npm run build)` → 0
- `(cd frontend && npx playwright test)` → all tests pass
- Security review: auth endpoints, JWT validation, RBAC, password hashing
- CI green on all jobs

## Critical files (references)

- `planning/MASTER_PLAN.md` lines 287-303 — Phase 2 definition
- `docs/LPA_BUSINESS_CASE.MD` Section 3.1 — Accounts acceptance criteria
- `CLAUDE.md` — COLA rules, fail-loudly, agent scope, process rules
- `backend/app/lib/result.py` — Result type for use case returns
- `backend/app/lib/errors.py` — DomainError base class
- `backend/app/infrastructure/config/env.py` — Settings with DATABASE_URL, JWT_SECRET, etc.
- `docker-compose.yml` — PostgreSQL service config
