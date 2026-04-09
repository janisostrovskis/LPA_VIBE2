# LPA Development Rulebook

**Version:** 1.0
**Status:** Enforced — all development work must follow these rules without exception.

This document defines the strict development process for the LPA platform. It is referenced by `CLAUDE.md` and governs all implementation work.

---

## B.1 Phased Development Flow

Every feature progresses through this pipeline. **No step may be skipped.**

```
PLAN → IMPLEMENT → TEST → SIMPLIFY → SECURITY REVIEW → GATE
```

1. **PLAN:** Read the relevant sub-plan from `planning/phase-NN/PLAN.md`. If no plan exists, create one using the template in section B.8 and wait for approval before writing code.
2. **IMPLEMENT:** Write code following COLA structure. Every file must belong to exactly one layer. Respect agent scope boundaries defined in `CLAUDE.md`.
3. **TEST:** All tests defined in the sub-plan's testing requirements must pass. Zero test failures tolerated.
4. **SIMPLIFY:** Run `/simplify` against all changed files. This checks for code duplication, unnecessary complexity, and reuse opportunities. All findings must be resolved. Re-run until clean.
5. **SECURITY REVIEW:** Complete the security review checklist (section B.3). All items must pass. Document results in `planning/phase-NN/SECURITY_REVIEW.md`.
6. **GATE:** Complete the testing gate document `planning/phase-NN/TESTING_GATE.md` using the template in section B.4. All criteria must pass to proceed to the next phase.

**Phase progression is strictly sequential.** Phase N+1 cannot begin until Phase N's gate is marked PASS.

---

## B.2 Agent Responsibilities and Handoff Protocol

Each agent owns a specific scope. An agent must **never** modify files outside its scope without explicit coordination through the handoff protocol.

### Ownership Table

| Agent | Owns (read/write) | Can Read | Cannot Touch |
|-------|-------------------|----------|-------------|
| **Database Agent** | `backend/app/infrastructure/database/`, `backend/app/domain/entities/`, `backend/app/domain/value_objects/`, `alembic/` | All layers | `frontend/`, payment adapters, API routes |
| **Backend Agent** | `backend/app/application/`, `backend/app/domain/rules/`, `backend/app/domain/events/`, `backend/app/domain/errors/`, `backend/app/lib/` | All layers | `frontend/`, infrastructure concrete implementations |
| **Frontend Agent** | `frontend/src/` (all directories) | Backend DTOs and API contracts | `backend/` (all) |
| **Payments Agent** | `backend/app/infrastructure/payments/`, `backend/app/application/ports/payment_gateway.py` | Domain entities, application use cases | Everything outside payment scope |
| **Security Agent** | `backend/app/api/middleware/`, `backend/app/infrastructure/config/`, `.gitignore`, `scripts/security_scan.py` | **Everything** (full read-only audit) | Does not fix directly — files issues for other agents |
| **i18n Agent** | `frontend/public/locales/`, translation-related components, `frontend/src/lib/i18n.ts` | All adapter components | Domain, application, infrastructure |
| **DevOps Agent** | Root config files (`docker-compose.yml`, `pyproject.toml`, `package.json`), `scripts/`, CI/CD config | Everything | Application code, domain logic |

### Handoff Protocol

When Agent A needs work done in Agent B's scope:

1. Agent A writes a handoff note in the phase plan: `HANDOFF: [Agent A] → [Agent B]: [exact task description with file paths and expected outcome]`
2. Agent B acknowledges the handoff, performs the work, runs tests within its scope.
3. Agent B writes: `HANDOFF COMPLETE: [task description] — [PASS/FAIL]`
4. If FAIL, Agent B documents the blocker and Agent A adjusts its approach.
5. **No agent may proceed past a gate until all handoffs in that phase are marked COMPLETE with PASS.**

---

## B.3 Security Review Checklist

Run after **every phase and subphase**. Every item is pass/fail. **A single fail blocks progression.**

### COLA Adherence

- [ ] No domain layer imports from application, API, or infrastructure
- [ ] No application layer imports from API or infrastructure concrete classes
- [ ] No infrastructure layer imports from API layer
- [ ] Every infrastructure dependency is accessed through a port interface (ABC)
- [ ] No FastAPI, SQLAlchemy, or Pydantic BaseModel imports in domain layer
- [ ] No React, Next.js, or Tailwind imports in backend service
- [ ] No business logic in frontend — all decisions made by backend API

### Secrets and Credentials

- [ ] No `.env` files committed (check `git log` history, not just current state)
- [ ] No hardcoded API keys, tokens, passwords, or connection strings in any source file
- [ ] `.env.example` contains only placeholder values (e.g., `STRIPE_KEY=sk_test_REPLACE_ME`)
- [ ] All secrets loaded through `backend/app/infrastructure/config/env.py` with Pydantic validation
- [ ] `env.py` raises `ValidationError` on missing required environment variables — app refuses to start
- [ ] No secrets in Docker Compose file (use env_file reference or environment variables)
- [ ] `.gitignore` includes: `.env`, `.env.*`, `!.env.example`

### Authentication and Authorization

- [ ] All `(auth)` frontend routes check session validity via backend API
- [ ] All `(admin)` frontend routes check admin role via backend API
- [ ] All backend API routes that require auth use middleware/dependency injection to validate JWT
- [ ] No sensitive data exposed in frontend JavaScript bundles (check build output)
- [ ] CORS configured to allow only the frontend origin
- [ ] JWT tokens have reasonable expiry and are not stored in localStorage (use httpOnly cookies)
- [ ] Webhook endpoints verify provider signatures before processing payloads

### Data Protection

- [ ] All user input validated with Pydantic schemas before reaching use cases
- [ ] SQL injection impossible — SQLAlchemy parameterized queries only, no `text()` without review
- [ ] XSS prevented — React default escaping, no `dangerouslySetInnerHTML` without sanitization and review
- [ ] GDPR: personal data fields identified and deletable via data export/deletion endpoints
- [ ] Audit log entries created for all sensitive operations (membership changes, payment actions, certification decisions, admin overrides)
- [ ] File uploads validated for type and size before storage

### Error Handling (Fail-Loudly Compliance)

- [ ] No bare `except:` or `except Exception: pass` anywhere in Python code
- [ ] No empty catch blocks in TypeScript code
- [ ] No `console.log` or `print()` used for error handling — structured logger only
- [ ] All errors propagated or explicitly handled with user-facing messages
- [ ] Payment errors never silently swallowed — failed payments result in visible status
- [ ] Every `# FAIL-QUIET-EXCEPTION:` has rationale, WARNING-level log, and plan approval
- [ ] No unhandled promise rejections in frontend code

---

## B.4 Testing Gate Template

Each phase has a `TESTING_GATE.md` in its planning subfolder. Use this template:

```markdown
# Testing Gate: Phase [NN] — [Phase Name]

## Date: YYYY-MM-DD
## Responsible agent: [agent name]

## Unit Tests
- [ ] All domain entity tests pass
- [ ] All use case tests pass
- [ ] All value object tests pass
- [ ] Backend coverage: ___% (minimum: 80% for domain, 70% for application)
- [ ] Frontend component tests pass (if applicable)

## Integration Tests
- [ ] Database repository tests pass against test PostgreSQL
- [ ] API route handler tests pass
- [ ] External service adapter tests pass (with mocks for external APIs)

## E2E Tests (if applicable for this phase)
- [ ] User flow tests pass in Playwright
- [ ] Tested in LV, EN, RU locales
- [ ] Mobile viewport tested (375px width)
- [ ] Desktop viewport tested (1440px width)

## Manual Verification
- [ ] Feature works as described in the phase sub-plan
- [ ] Error states display correctly (fail loudly — errors are visible, not swallowed)
- [ ] Accessibility: keyboard navigation works, screen reader labels present

## /simplify Review
- [ ] `/simplify` ran on all changed files
- [ ] Zero remaining findings
- [ ] No duplicated logic across files
- [ ] No file exceeds 2,000 lines (1,500-line warning threshold respected)

## Security Review
- [ ] Full checklist from section B.3 completed
- [ ] All items passed
- [ ] Results documented in SECURITY_REVIEW.md

---

## GATE RESULT: [ PASS / FAIL ]

## If FAIL — blocking issues:
1. [description]
2. [description]
```

---

## B.5 Fail-Loudly Principle

**Default rule:** Every error must surface to the nearest responsible party (user, admin, developer, or log). Silent failure is a bug.

### Enforcement

1. **No bare except / empty catch.** Python: Ruff rule `E722` + custom rule for `pass`-only exception handlers. TypeScript: ESLint `no-empty` with `allowEmptyCatch: false`. Pre-commit hook rejects violations.

2. **No unhandled promises.** TypeScript: ESLint `@typescript-eslint/no-floating-promises` set to `error`.

3. **Result type for expected failures.** Use cases return `Result[T, DomainError]` instead of raising exceptions for expected business-rule violations:

   ```python
   # backend/app/lib/result.py
   @dataclass(frozen=True)
   class Ok(Generic[T]):
       value: T

   @dataclass(frozen=True)
   class Err(Generic[E]):
       error: E

   Result = Ok[T] | Err[E]
   ```

   The API layer inspects the result and returns appropriate HTTP status + structured JSON error.

4. **Environment validation at startup.** `backend/app/infrastructure/config/env.py` uses Pydantic `BaseSettings`. If any required variable is missing or malformed, the application refuses to start with a clear error naming the problem:
   ```
   ERROR: Missing required environment variable: STRIPE_WEBHOOK_SECRET
   ```

5. **Payment operations are never fire-and-forget.** Every payment call must `await` confirmation and handle all failure modes explicitly. A payment failure must result in a visible status change:
   - Enrollment stays `PENDING` (never `CONFIRMED`) until webhook confirms
   - Membership is not activated until payment succeeds
   - Failed payment triggers notification to user AND admin

6. **No fallback defaults for critical config.** Database URL, secret keys, payment credentials — if they are missing, the app crashes at startup. Do not invent defaults.

### Exception Process

If a developer believes a specific case genuinely warrants a silent fallback:

1. Add a code comment: `# FAIL-QUIET-EXCEPTION: [rationale]`
2. Log the suppressed error at `WARNING` level minimum via structured logger
3. Document the exception in the current phase plan with approval
4. Security agent reviews the exception during the phase security review
5. Exception must be re-evaluated every 3 phases — if the underlying issue is fixable, fix it and remove the exception

---

## B.6 /simplify + Security Review Sequence

After each **major phase** completion (and recommended after each subphase):

```
Step 1: /simplify
   → Run /simplify on all files changed in the phase
   → Review output
   → Fix all identified issues (duplication, unnecessary complexity, reuse opportunities)
   → Re-run /simplify until output is clean (zero findings)

Step 2: Security Review
   → Complete every item in the B.3 checklist
   → Document results in planning/phase-NN/SECURITY_REVIEW.md
   → Fix all failures
   → Re-run checklist until all items pass

Step 3: Testing Gate
   → Fill in planning/phase-NN/TESTING_GATE.md using the B.4 template
   → All sections must be PASS
   → If any section is FAIL, loop back to Step 1

Step 4: Proceed
   → Only when Steps 1-3 are all clean: begin next phase
```

**There is no shortcut through this sequence.** If Step 3 fails, you go back to Step 1, not Step 2.

---

## B.6.2 Simplify Receipt Artifacts

Every handoff that claims `simplify — PASS` in `planning/phase-NN/HANDOFF_LOG.md` MUST also produce a small artifact file documenting what was reviewed and what was found. Forward-only — effective 2026-04-09. Receipts before that date are not retroactively required.

**Artifact location:** `planning/phase-NN-<name>/simplify-receipts/<subphase>-<agent>.md`

**Schema:**

```
# Simplify receipt — <subphase> <agent> <ISO date>

## Files reviewed
- path1
- path2

## Findings (if any)
- location:line — description — action taken

## Verdict
<PASS — clean | N findings addressed | WAIVED — reason>
```

**Why:** before this rule, `simplify — PASS` in a HANDOFF_LOG entry was unverifiable prose. The artifact requirement raises the floor — an empty file list fails the validator, so an agent has to at least name the files it actually reviewed. `scripts/check_handoff_log.py` enforces artifact presence for source-touching entries dated 2026-04-09 or later. Entries marked `retrofit: true` and entries claiming `simplify — waived/N/A` are exempt.

---

## B.6.1 Rule 3 Verification — Pre-commit Mandate

Every handoff records a "Rule 3 verification" sequence in `planning/phase-NN/HANDOFF_LOG.md` listing the commands that prove the work is correct. Agents historically wrote their own command lists, which drifted from the pre-commit pipeline — `postgresql+psycopg://` and stray test-fixture DB URLs both slipped past Rule 3 in Phase 0 only to be caught later by `pre-commit run`.

**Rule (effective 2026-04-09):** the Rule 3 sequence in any handoff that touches source files MUST end with a backtick-wrapped `pre-commit run --files <space-separated changed files>` command (or `--all-files`) reporting exit 0. The pre-commit pipeline is the source of truth for acceptance; agent-authored commands are additive, not a substitute.

`scripts/check_handoff_log.py` enforces this. Entries dated before 2026-04-09 and entries marked `retrofit: true` are exempt.

---

## B.7 File Size Enforcement

- **Hard limit:** 2,000 lines per `.py`, `.ts`, or `.tsx` file.
- **Warning threshold:** 1,500 lines — split proactively when you hit this.
- **Enforcement:** Pre-commit hook runs `scripts/check_file_size.py`. A commit containing a file exceeding 2,000 lines is **rejected** with a message naming the offending file and its line count.
- **CI enforcement:** The same check runs in CI. A PR with an oversized file cannot merge.
- **Exclusions:** Only auto-generated files are exempt: Alembic migration files, Prisma client output, compiled/bundled output. The exemption list is hardcoded in `scripts/check_file_size.py` and reviewed by the security agent.

### Splitting strategies when a file approaches the limit

| Situation | Split Strategy |
|-----------|---------------|
| Entity file growing | Extract value objects, extract validation into `rules/` |
| Use case file growing | Break into smaller composable use cases |
| Component file growing | Extract sub-components, extract hooks |
| Repository file growing | Split read queries from write operations |
| API route file growing | Split by HTTP method or sub-resource |
| Model file growing | Split into separate model files per aggregate |

---

## B.8 Planning Document Structure

### Folder layout

```
planning/
├── MASTER_PLAN.md                        # Top-level 10-phase roadmap
├── phase-00-foundation/
│   ├── PLAN.md                           # Detailed sub-plan for this phase
│   ├── TESTING_GATE.md                   # Filled in at phase completion
│   └── SECURITY_REVIEW.md               # Filled in at phase completion
├── phase-01-design-system/
│   ├── PLAN.md
│   ├── sub-01-tailwind-tokens.md         # Sub-phase plan (optional granularity)
│   ├── sub-02-ui-primitives.md
│   ├── TESTING_GATE.md
│   └── SECURITY_REVIEW.md
├── phase-02-accounts/
│   ├── PLAN.md
│   ├── sub-01-database-schema.md
│   ├── sub-02-domain-entities.md
│   ├── sub-03-use-cases.md
│   ├── sub-04-api-routes.md
│   ├── sub-05-ui-pages.md
│   ├── TESTING_GATE.md
│   └── SECURITY_REVIEW.md
└── ... (one subfolder per phase)
```

### PLAN.md template

```markdown
# Phase [NN]: [Phase Name]

## Objective
[One paragraph — what this phase delivers and why it matters]

## Prerequisites
[What must be complete before this phase starts, including prior phase gate status]

## Deliverables
[Numbered list of concrete outputs: files to create, features to implement, configs to set up]

## Sub-phases (if applicable)
[Ordered list of sub-phases with references to their own plan files]
1. `sub-01-name.md` — [brief description]
2. `sub-02-name.md` — [brief description]

## Agent Assignments
[Which agent owns which deliverable from the list above]

## Handoffs
[Pre-identified cross-agent dependencies]
- HANDOFF: [Agent A] → [Agent B]: [task description]

## Testing Requirements
[Specific tests that must pass for the gate — mapped to acceptance criteria]

## Acceptance Criteria
[Copied or referenced from docs/LPA_BUSINESS_CASE.MD sections that this phase addresses]

## Risks and Mitigations
[Known challenges and how to handle them]
```

### SECURITY_REVIEW.md template

```markdown
# Security Review: Phase [NN] — [Phase Name]

## Date: YYYY-MM-DD
## Reviewer: Security Agent

## COLA Adherence
- [ ] Item 1...
- [ ] Item 2...
(use full checklist from B.3)

## Secrets and Credentials
- [ ] ...

## Authentication and Authorization
- [ ] ...

## Data Protection
- [ ] ...

## Error Handling
- [ ] ...

## Findings
[List any issues found, even if already fixed]

## REVIEW RESULT: [ PASS / FAIL ]
```

---

## Appendix: Quick Reference

### The non-negotiable rules (for quick checking)

1. Every file belongs to exactly one COLA layer
2. Domain layer has zero framework imports
3. No file exceeds 2,000 lines
4. No secrets in git — ever, including in history
5. No silent error handling — fail loudly or document the exception
6. Every phase ends with: /simplify → security review → testing gate
7. No agent modifies files outside its scope without a handoff
8. Frontend never contains business logic
9. Payment confirmation required before any status change
10. All three languages (LV/EN/RU) tested at every gate