# Testing Gate — Phase 02 Accounts & Authentication

**Date:** 2026-04-10
**Final commit:** `fae518d` (02f) + a11y fix pending
**CI run:** 24244294245 — GREEN

## Test Summary

| Suite | Count | Status |
|-------|-------|--------|
| Backend pytest (domain) | 61 | ALL PASS |
| Backend pytest (application) | 22 | ALL PASS |
| Backend pytest (infrastructure) | 16 | ALL PASS |
| Backend pytest (API) | 6 | ALL PASS |
| Backend pytest (lib) | 36 | ALL PASS |
| **Backend total** | **141** | **ALL PASS** |
| Frontend Vitest unit tests | 70 | ALL PASS |
| Playwright e2e — smoke | 1 | PASS |
| Playwright e2e — i18n | 4 | PASS |
| Playwright e2e — routes | 36 | PASS |
| Playwright e2e — a11y (axe-core) | 36 | PASS |
| **Frontend total** | **147** | **ALL PASS** |
| **Grand total** | **288** | **ALL PASS** |

## Backend Test Breakdown (141 tests)

| File | Tests | What it covers |
|------|-------|----------------|
| test_email_vo.py | 13 | Email VO validation, normalization, immutability |
| test_locale_vo.py | 8 | Locale StrEnum values, membership |
| test_auth_rules.py | 16 | Password strength, magic link expiry/boundary |
| test_auth_errors.py | 20 | Error codes, inheritance, immutability |
| test_domain_events.py | 7 | MemberRegistered, MemberLoggedIn fields |
| test_repositories.py | 16 | Entity-model round-trip, abstract conformance |
| test_jwt_service.py | 8 | JWT issue/validate, expiry, tamper, claims |
| test_password_service.py | 6 | Hash/verify round-trip, wrong password, salt |
| test_register.py | 4 | Register success, duplicate, weak password, invalid email |
| test_login.py | 4 | Login success, wrong password, unknown email, magic-link-only |
| test_auth_routes.py | 6 | HTTP endpoints: health, register, duplicate, login, wrong pw, unknown |
| test_env.py | 3 | Settings parsing, cache |
| test_errors.py | 12 | Error taxonomy |
| test_logger.py | 6 | Structured logging |
| test_result.py | 12 | Result type Ok/Err |

## Frontend Test Breakdown

| Suite | Tests | What it covers |
|-------|-------|----------------|
| Vitest unit (11 files) | 70 | UI components, layout components |
| Playwright smoke | 1 | /lv renders |
| Playwright i18n | 4 | 3 locales + root redirect |
| Playwright routes | 36 | 12 routes x 3 locales |
| Playwright a11y | 36 | axe-core WCAG 2.2 AA |

## Build Verification

- `(cd backend && python -m mypy app/)` → 0 errors (69 source files)
- `(cd backend && ruff check app/)` → 0 errors
- `(cd frontend && npm run build)` → 46 static pages
- TypeScript strict mode: clean (no `any`, no `@ts-ignore`)

## WCAG 2.2 AA Compliance

- 36 axe-core audits across all routes and locales
- Zero critical violations
- Zero serious violations (after underline fix on join/login inline links)

## Phase 02 Coverage Summary

| Sub-phase | What was tested |
|-----------|----------------|
| 02a | Email VO validation, Locale enum, entity round-trips |
| 02b | Auth rules (password, magic link), error taxonomy, domain events |
| 02c | Repository mapping fidelity, JWT issue/validate, password hash/verify |
| 02d | Register + login use cases with mocked ports |
| 02e | HTTP endpoints via httpx AsyncClient with dependency overrides |
| 02f | Frontend build, Vitest components, Playwright a11y on auth pages |
