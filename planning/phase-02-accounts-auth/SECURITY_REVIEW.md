# Security Review — Phase 02 Accounts & Authentication

**Date:** 2026-04-10
**Reviewer:** security-agent + main session (agent had write issues)
**Scope:** All files under `backend/app/`, `backend/alembic/`, `frontend/src/lib/`, frontend auth pages

## Summary

**PASS with caveats.** Core auth implementation is sound — JWT HS256 with algorithm pinning, bcrypt password hashing, parameterized SQL queries, Result-based error handling. Three items flagged for Phase 03 attention (not blockers).

## Checklist

| # | Check | Result | Notes |
|---|-------|--------|-------|
| 1 | JWT configuration | PASS | HS256 algorithm pinned in `jwt.decode(algorithms=["HS256"])`. Expiry set via `exp` claim. Secret injected via constructor, read from `JWT_SECRET` env var in dependencies.py. |
| 2 | Password hashing | PASS | bcrypt with auto-salt via `bcrypt.gensalt()`. `bcrypt.checkpw()` is timing-safe. No plaintext storage. |
| 3 | Magic link security | PASS | `secrets.token_urlsafe(32)` provides 256-bit entropy. 15-minute expiry enforced. Single-use via `used` flag with atomic consume. |
| 4 | SQL injection | PASS | All queries use SQLAlchemy ORM with parameterized binds. No raw SQL string concatenation. |
| 5 | XSS vectors | PASS | Zero `dangerouslySetInnerHTML`, `innerHTML`, `eval`, or `document.write`. All text via React JSX (auto-escaped) or next-intl translations. |
| 6 | CSRF/CORS | PASS (dev) | CORS allows `http://localhost:3000` only. Production CORS origins should be tightened in Phase 09 deployment. |
| 7 | Auth bypass | PASS | All protected routes use `Depends(require_member_id)` which chains through `require_auth` → JWT validation. No unprotected gaps in member/org routes. |
| 8 | Error information leakage | PASS | `_errors.py` maps DomainError to HTTP status + `detail` message only. No stack traces exposed. |
| 9 | Secrets in source | PASS | Dev JWT secret has `pragma: allowlist secret`. No real credentials in source. `env.py` validates required vars at startup. |
| 10 | Token storage | PASS | Frontend `auth-context.tsx` stores JWT in React state (memory). Not in localStorage or cookies. XSS-safe. |
| 11 | Input validation | PASS | Email validated via regex VO. Password strength checked (8+ chars, upper, lower, digit). Locale validated against Locale enum. CHECK constraints in DB. |
| 12 | Rate limiting | CAVEAT | No rate limiting on login/register/magic-link endpoints. Not a blocker for Phase 02 (no public deployment), but MUST be added before production (Phase 09). |
| 13 | RBAC | CAVEAT | Role data exists in `user_roles` table with CHECK constraint, but no endpoint-level role enforcement yet. All authed endpoints just check "is authenticated" not "has role X". Role-based access should be wired in Phase 03+ as admin routes are added. |
| 14 | Dependency audit | PASS | `pip-audit`: 0 production vulnerabilities (virtualenv 20.26.2 has PYSEC-2024-187 but is dev-only). `npm audit --omit=dev`: 0 vulnerabilities. |
| 15 | GDPR export | PASS | `GET /me/export` requires auth, returns all member fields as JSON dict. Endpoint is auth-protected. |

## Findings

### F1 — No rate limiting (CAVEAT, not blocker)
Login, register, and magic-link-request endpoints have no rate limiting. An attacker could brute-force passwords or enumerate emails via timing differences. This is acceptable for Phase 02 (local dev only) but MUST be addressed before any public deployment.
- **Remediation:** Add rate limiting middleware (e.g., `slowapi` or custom) in Phase 09 (deployment).

### F2 — User enumeration via magic link (LOW)
`RequestMagicLink` returns `Err(NotFoundError)` when email is not registered. This reveals whether an email exists in the system. For magic link, a generic "if registered, you'll receive an email" response would be safer.
- **Remediation:** Change `RequestMagicLink` to return `Ok(None)` regardless of email existence. Log the miss server-side.

### F3 — JWT refresh has no rotation (LOW)
`RefreshToken` validates the old token and issues a new one with the same subject but doesn't invalidate the old token. Both tokens remain valid until natural expiry. Acceptable for Phase 02 but token revocation should be considered for Phase 03+.
- **Remediation:** Add a token blacklist or use short-lived access tokens + longer-lived refresh tokens stored server-side.

## Phase 03 Readiness

Core auth is secure. The three caveats (rate limiting, user enumeration, token rotation) are standard hardening items that don't block feature development but must be resolved before public deployment.
