# Phase 02 — Accounts & Authentication — Retrospective

**Date:** 2026-04-10
**Phase:** 02 (Accounts & Authentication)
**Sub-phases delivered:** 02a, 02b, 02c (parallel), 02d, 02e, 02f
**Agents involved:** database-agent, backend-agent, frontend-agent

---

## 1. Phase Summary

| Metric | Value |
|--------|-------|
| Sub-phases | 6 (02a–02f; 02g = close gates) |
| Handoffs dispatched | 7 (02a-H1, 02b-H1, 02c-H1, 02c-H2, 02d-H1, 02e-H1, 02f-H1) |
| Parallel handoffs | 1 pair (02c-H1 + 02c-H2) |
| Backend tests at close | 141 (pytest) |
| Frontend tests at close | 70 (vitest) |
| Scope overrides (estimated) | ~20 (concentrated in 02d and 02e) |
| First-dispatch pass rate | 7/7 (all HANDOFF COMPLETE — PASS) |
| Main-session fixup sessions | Every sub-phase except 02b |

All 7 handoffs reported PASS. However, every handoff except 02b required at least one main-session fixup before the Rule 3 terminal `pre-commit` step could exit 0. The "PASS" designations reflect eventual state after fixups, not clean first-dispatch.

---

## 2. Dispatch Efficiency

| Sub-phase | Dispatched | Fixups needed by main session | Root cause |
|-----------|-----------|-------------------------------|------------|
| 02a | database-agent | Yes — scope.yaml alembic path; test exception type; unused type: ignore; quoted annotation | scope.yaml out of date; agent knowledge gap |
| 02b | backend-agent | Minor — ruff ran over wrong test dirs | Agent ran `ruff --fix tests/` instead of scoped subdirs |
| 02c-H1 | database-agent | Yes — rowcount mypy attr-defined | Known SQLAlchemy async typing gap |
| 02c-H2 | backend-agent | Yes — import sorting (I001) | ruff import order not followed during authoring |
| 02d | backend-agent | Yes — mypy disallow_any_explicit + Pydantic BaseModel; ruff S105; E501 | Pydantic DTOs incompatible with mypy strict disallow_any_explicit; no doc rule |
| 02e | backend-agent | Yes — FastAPI 204/None; deprecated HTTP constant; E402 import ordering; TypeVar migration; main.py not in scope; JWT pragma syntax | Multiple FastAPI footguns; scope.yaml missing main.py |
| 02f | frontend-agent | Yes — translation keys omitted; useSearchParams Suspense; a11y inline links | Agent brief didn't require translation delivery; React 18 Suspense boundary gap |

---

## 3. Friction Analysis

### F1 — scope.yaml gaps accumulate silently until dispatch

**Symptom:** 02a blocked because `alembic/**` in scope.yaml was root-relative (should be `backend/alembic/**`). 02c-H1 needed `application/ports/*` for database-agent. 02e needed `backend/app/main.py` for backend-agent (added as a post-dispatch override). Each gap required a scope override from main session mid-handoff or between handoffs.

**Root cause:**
1. scope.yaml is authored once at project start and amended reactively after dispatch failures.
2. No pre-phase audit step verifies that scope.yaml covers all files listed in the PLAN.md deliverables.
3. Agents cannot self-amend scope.yaml (correctly — it's a governance file) so every gap becomes a main-session interrupt.

**Classification:** Systemic — occurred in 02a, 02c, and 02e across three different agents. Same pattern observed in Phase 01.

**Cross-platform check:** N/A (process document amendment, no commands).

**Fix location:** `docs/DEVELOPMENT_RULEBOOK.MD` — add a "Pre-phase scope.yaml audit" step to the phased development flow (B.1), requiring main session to diff PLAN.md deliverable file list against scope.yaml allow patterns before dispatching the first handoff.

---

### F2 — Pydantic BaseModel + mypy `disallow_any_explicit` — recurring conflict

**Symptom:** 02d backend-agent produced DTOs using `Pydantic BaseModel`. mypy strict mode's `disallow_any_explicit` flag flags `Any` usages that Pydantic's own internals require. Agent had to add a per-module `# type: ignore` override or pyproject.toml override for `app.application.dto.*`. 02e extended the override to `app.api.routes.*`.

**Root cause:**
1. mypy strict mode's `disallow_any_explicit` is incompatible with Pydantic v2 BaseModel field declarations that use `Any` (e.g., `Optional[Any]`, `Dict[str, Any]`).
2. The backend-agent.md describes DTOs as "Pydantic models" and instructs mypy strict compliance, but does not document how to reconcile the two.
3. Without upfront guidance, the agent first writes clean Pydantic DTOs, then discovers the mypy conflict, then applies a per-module override — costing a main-session fixup each time.

**Classification:** Systemic — will recur in every phase that adds DTOs or route models. The override pattern is already in pyproject.toml; the gap is that agents don't know to apply it proactively.

**Cross-platform check:** N/A — pyproject.toml edit; platform-agnostic.

**Fix location:** `.claude/agents/backend-agent.md` — add a note under the DTOs section documenting that `app.application.dto.*` and `app.api.routes.*` carry a pyproject.toml mypy per-module override for `disallow_any_explicit = false`, and that new DTO/route files in these packages should not attempt to satisfy `disallow_any_explicit`.

---

### F3 — Security-scan pragma placement breaks syntax inside parenthesized calls

**Symptom:** 02d/02e — `detect-secrets` / gitleaks pragma comments (`# pragma: allowlist secret`) need to be on the same line as the detected string. Inside multi-line parenthesized function calls, placing the pragma comment inline caused Python syntax errors when the closing parenthesis was on the next line. Multiple back-and-forth fixes needed.

**Root cause:**
1. No existing documentation tells agents where to place the pragma relative to a parenthesized call.
2. The intuitive placement (end of string line) is correct only when the string is a standalone assignment, not when it's an argument inside an open paren.
3. Python allows inline comments mid-expression, but only as trailing comments on each logical line — the agent was occasionally placing them after the closing paren rather than on the string's own line.

**Classification:** Systemic — any phase that contains test passwords or JWT secret defaults will hit this. Already repeated across 02d and 02e.

**Cross-platform check:** N/A — code style rule, platform-agnostic.

**Fix location:** `.claude/agents/backend-agent.md` — add a concrete example of correct vs incorrect pragma placement for multi-line function calls.

---

### F4 — FastAPI 204 + `-> None` return annotation assertion error

**Symptom:** 02e — FastAPI route with `status_code=204` and return type annotation `-> None` triggers an internal assertion error at app startup (`assert response_model is not None`). Fixed by explicitly passing `response_model=None` to the decorator.

**Root cause:**
1. FastAPI's behavior for 204 routes changed between versions. The `-> None` annotation is not sufficient — `response_model=None` must be explicit.
2. No project rule documented this footgun. The agent wrote idiomatic-looking `-> None` code, which is correct for most response types but not for 204.

**Classification:** Systemic — every future agent writing a 204 (DELETE, logout, etc.) route will hit this unless the rule is documented.

**Cross-platform check:** N/A — code pattern rule, platform-agnostic.

**Fix location:** `.claude/agents/backend-agent.md` — add a FastAPI footguns section documenting that 204 routes require explicit `response_model=None` in the decorator, not just `-> None`.

---

### F5 — Frontend agent omits translation keys for new pages

**Symptom:** 02f — frontend-agent delivered auth pages (join, login, profile) without adding any keys to `frontend/public/locales/{lv,en,ru}/common.json`. All user-facing strings were either hardcoded or referenced keys that didn't exist. Main session added translation keys for all 3 locales after the fact.

**Root cause:**
1. `frontend/public/locales/` is listed in frontend-agent.md under "You MUST NOT touch" because it is i18n-Agent scope.
2. The PLAN.md 02f deliverables explicitly listed the locale JSON files as a required output.
3. The conflict between agent scope boundary and plan deliverable was not resolved at plan time. The frontend-agent correctly respected its scope boundary but left a gap.
4. The intended solution (dispatch i18n-agent separately for translations) was never planned — the 02f handoff brief implicitly assumed frontend-agent would handle it.

**Classification:** Systemic — will recur on every frontend sub-phase that introduces new UI pages. The frontend-agent/i18n-agent boundary means every new page requires either a parallel i18n handoff or an explicit brief instruction that i18n-agent handles translations.

**Cross-platform check:** N/A — process rule, platform-agnostic.

**Fix location:** `CLAUDE.md` — add a rule under the Multilingual section: any sub-phase that ships new frontend pages must include a parallel i18n-agent handoff for the translation keys. The frontend-agent brief must not list locale JSON files as its deliverable. Update also `planning/` conventions note in `docs/DEVELOPMENT_RULEBOOK.MD`.

**Fix also location:** `.claude/agents/frontend-agent.md` — clarify that the agent must NOT write to `frontend/public/locales/` and must instead note any missing translation keys in its handoff Notes so the orchestrator can dispatch i18n-agent.

---

### F6 — a11y inline link underline missing on auth pages

**Symptom:** 02f — links inside paragraph text on login/join pages lacked visible underline, failing WCAG 2.2 AA non-text contrast requirement for inline links. Axe CI check flagged these after the handoff. Fixed by main session adding `underline` class to inline anchor elements.

**Root cause:**
1. The frontend-agent.md accessibility rules say "focus states on all interactive elements" but do not call out the inline-link underline requirement specifically.
2. Tailwind CSS removes default link underlines globally via preflight CSS. Agents writing `<a>` tags naturally omit `underline` because Tailwind strips the browser default.
3. The design language doc's links section specifies underline for inline body links but the agent brief references the design language without highlighting this specific constraint.

**Classification:** Systemic — Tailwind preflight strips underlines globally, so any new inline link without `underline` class will fail a11y. This will recur on every page with inline anchor text.

**Cross-platform check:** N/A — CSS rule, platform-agnostic.

**Fix location:** `.claude/agents/frontend-agent.md` — add a specific a11y rule: inline anchor elements (links within paragraph text) must include the `underline` class. Tailwind preflight removes default underlines; omitting the class fails WCAG 2.2 AA non-text contrast.

---

### F7 — Cross-sub-phase simplify gaps not caught by per-handoff simplify

**Symptom (from memory note):** Per-handoff simplify in 02a and 02b each passed, but a cross-sub-phase simplify run after both were complete found additional inconsistencies: missing re-exports in `__init__.py`, a tautology function (`is_magic_link_used` that just returned the field value), and missing DB CHECK constraints that the entity dataclass enforced but the model did not.

**Root cause:**
1. Per-handoff simplify can only see the files written in that handoff. Cross-cutting issues — where the database model and the domain entity diverge, or where a public re-export is missing — only become visible when both sides exist.
2. No rule requires a cross-sub-phase simplify checkpoint after parallel handoffs land or after every 2–3 sequential handoffs.

**Classification:** Systemic — parallel dispatch (02c) is the standard pattern for infra work. Any time two agents independently implement complementary pieces, cross-cutting simplify gaps are expected.

**Cross-platform check:** N/A — process rule, platform-agnostic.

**Fix location:** `docs/DEVELOPMENT_RULEBOOK.MD` — add to B.1 flow: after every parallel dispatch pair lands, main session must run simplify across the union of changed files from both handoffs before proceeding.

---

## 4. Amendments Applied

### `.claude/agents/backend-agent.md`
- Added FastAPI footguns section documenting: 204 routes require `response_model=None`; `HTTPBearer()` must appear after all imports (E402); TypeVar syntax should use PEP 695 `type` parameter syntax for Python 3.12+.
- Added Pydantic + mypy note: `app.application.dto.*` and `app.api.routes.*` have `disallow_any_explicit = false` in pyproject.toml; new files in these packages should not attempt to satisfy that flag.
- Added security pragma example showing correct placement inside multi-line parenthesized calls.

### `.claude/agents/frontend-agent.md`
- Added a11y inline link rule: inline `<a>` elements in paragraph text must include `underline` class (Tailwind preflight strips browser default).
- Added explicit note: MUST NOT write to `frontend/public/locales/` — note missing translation keys in handoff Notes for i18n-agent dispatch.
- Added `useSearchParams()` / Suspense rule: any component using `useSearchParams()` must be wrapped in a `<Suspense>` boundary because Next.js App Router opts the page out of static rendering without it.

### `docs/DEVELOPMENT_RULEBOOK.MD`
- Added pre-phase scope.yaml audit step to B.1 flow.
- Added cross-sub-phase simplify checkpoint rule to B.1 flow.
- Added note to parallel dispatch section: any phase plan listing new frontend pages must include a parallel i18n-agent handoff.

### `CLAUDE.md`
- Added rule to Multilingual section: every sub-phase shipping new frontend pages must dispatch i18n-agent in parallel to deliver translation keys. Frontend-agent does not own locale JSON files.

---

---

## Addendum — Post-Close Session (2026-04-11)

A follow-on session after Phase 02 formal close delivered:
- Security-finding remediations (4 findings: org invite auth, magic link enumeration, org ownership, JWT refresh is_active check)
- Amazon SES email adapter integration
- Simplify fixes found during that session (RoleName enum, type:ignore cleanup, validation ordering in invite_member)

Three additional friction patterns were identified and process documents were amended.

### FA1 — `/security-review` ran against an empty diff

**Symptom:** `/security-review` was invoked after all changes were already committed. The slash command runs `git diff` internally, which returned nothing on a clean working tree. The review report covered zero files. The user had to re-invoke with an explicit instruction to look at committed Phase 2 code.

**Root cause:** The `/security-review` slash command is not project-defined — it uses the working-tree diff as its scope. No rule existed telling the orchestrator to pass a commit range to security-agent when reviewing already-committed work.

**Classification:** Systemic — any time the orchestrator schedules a security review after (rather than before) a commit, this will recur. The pattern of committing first and reviewing second is common in ad-hoc fix sessions.

**Fix applied:** Added a "Scoping the Review to the Right Code" section to `.claude/agents/security-agent.md` documenting how to use `git diff <base>..<tip>` when the working tree is clean, and instructing the orchestrator to pass the commit range in the dispatch brief.

---

### FA2 — Docker port conflicts required two failed `docker compose up` attempts

**Symptom:** `/dev` built and started Docker Compose without first checking whether ports 5432 and 3000 were free. Both were in use (local PostgreSQL on 5432, another server on 3000). The command failed twice; ports were manually remapped between attempts.

**Root cause:** The `/dev` command's build step ran before any port-conflict check. The command's summary also hardcoded the ports instead of reflecting actual (possibly remapped) host ports.

**Classification:** Systemic — the user regularly develops with a local PostgreSQL instance running. Port 5432 will almost always be occupied on this machine. Port 3000 is commonly used by other dev servers.

**Fix applied:** Added a step 3 "Port conflict check" to `.claude/commands/dev.md` instructing the command to probe ports 5432, 3000, and 8001 with `lsof` before starting Docker, and remap host-side ports in `docker-compose.yml` if any conflict is detected. Updated the report step to use actual (possibly remapped) port values.

---

### FA3 — Ad-hoc work close sequence skipped until user prompted

**Symptom:** After completing the security-fix batch (4 findings) and the SES integration, neither simplify nor security review nor efficiency retrospective was run. The user had to explicitly ask "was the agentic flow implemented with simplify, security and efficiency?" When simplify was then run, it found real issues (stringly-typed role names, unnecessary type:ignore, validation ordering).

**Root cause:** The "After completing a phase" close sequence in `CLAUDE.md` is framed as a phase-level obligation. Ad-hoc work that does not map to a formal sub-phase has no documented close requirement, so the orchestrator treated it as optional.

**Classification:** Systemic — ad-hoc fix sessions and mid-cycle integrations will recur throughout the project. The omission of simplify resulted in real code quality issues landing without review.

**Fix applied:** Added a new "After completing ad-hoc work" section to `CLAUDE.md` immediately after the phase close sequence, documenting that any committed batch of code changes — regardless of whether it is a formal sub-phase — requires simplify + security-agent review + test confirmation before moving on.

---

## 5. Phase 03 Readiness

All functional deliverables are in place. No blocking process gaps remain for Phase 03 start, with one note:

**Scope.yaml pre-audit:** Before dispatching the first Phase 03 handoff, main session must diff the PLAN.md deliverable list against scope.yaml allow patterns (per the new B.1 rule added above). Phase 03 (Memberships & Payments) will introduce `backend/app/infrastructure/payments/` and `backend/app/application/ports/payment_gateway.py` — the payments-agent allow list in scope.yaml already covers these, but any new ports or infrastructure files specific to Phase 03 should be verified before dispatch.

**i18n parallel handoffs:** Phase 03 will add membership-related UI pages. Plan must include a parallel i18n-agent handoff alongside the frontend-agent handoff for those pages.

**mypy override pre-applied:** The `disallow_any_explicit = false` override is now in pyproject.toml for `app.application.dto.*` and `app.api.routes.*`. Any new Phase 03 DTO or route module in these packages automatically inherits the override — no post-dispatch fixup needed.
