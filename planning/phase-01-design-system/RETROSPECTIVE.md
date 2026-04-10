# Retrospective — Phase 01 Design System

**Date:** 2026-04-10
**Sub-phases:** 01a — 01f (Design System & Layout Shell)
**Efficiency Agent session:** current

---

## Phase Summary

| Metric | Value |
|--------|-------|
| Sub-phases | 6 (01a, 01b, 01c, 01d, 01e, 01f) |
| Handoffs | 9 (01a-H1, 01b-H0/H1/H2, 01c-H1/H2, 01d-H1, 01e-H1/H2, 01f-H1/H2) |
| Vitest tests shipped | 70 |
| Playwright tests shipped | 77 |
| Total tests | 147, all green |
| Static pages generated | 40 (12 routes x 3 locales + not-found) |
| WCAG violations | 0 critical/serious |
| CI run | 24233999945 — GREEN |
| Commits | 8 (01a–01f + 1 simplify cleanup) |
| Scope overrides | 18 (see breakdown below) |

---

## Dispatch Efficiency

| Sub-phase | Handoffs | First-dispatch successes | Overrides by main session | Notes |
|-----------|----------|--------------------------|---------------------------|-------|
| 01a | H1 | 0 of 1 | 0 | Blocked by missing simplify-receipts scope; re-dispatched after fix |
| 01b | H0+H1 (parallel), H2 | H0: 1/1; H1: 1/1; H2: 0/1 | 3 | H2 required ~4 agent dispatches + 3 main-session overrides |
| 01c | H1+H2 (parallel) | 1/1; H2: 1/1 (after 2 overrides) | 2 | 2 noUncheckedIndexedAccess fixes to Modal.tsx after H2 |
| 01d | H1 | Partial (agent ran out of context) | 7 | Agent produced code but couldn't fix jest-dom test failures |
| 01e | H1+H2 sequential | 1/1; 1/1 | 0 | Clean |
| 01f | H1+H2 (parallel) | 1/1; 1/1 | 0 | Clean |

**First-dispatch success rate (handoffs landing without main-session overrides):** 6 of 9 handoffs (67%).
Friction was concentrated in 01b-H2 (3 overrides), 01c (2 overrides), and 01d (7 overrides). 01e and 01f were clean.

---

## Friction Analysis

### F1 — simplify-receipts scope gap (01a, 01b)
- **Symptom:** 01a-H1 blocked mid-execution; could not write `planning/.../simplify-receipts/` file.
- **Root cause:** `planning/**/simplify-receipts/**` was missing from all shipping-agent allow lists in `.claude/scope.yaml`. No sub-phase in Phase 00 had required agents to write receipts, so the latent gap was never hit.
- **Classification:** Systemic — would have blocked every first simplify-PASS claim in Phase 01.
- **Fix applied during phase:** scope.yaml amended mid-01b to add path to all 7 agent allow lists.
- **Permanent:** Yes. Scope.yaml is correct. No further amendment needed.

### F2 — Bash cwd deadlock (01b-H2)
- **Symptom:** Bare `cd frontend && npm install` leaked cwd; subsequent hook invocation resolved `scripts/hooks/pretool_scope_guard.py` as `frontend/scripts/hooks/...` (non-existent). Python exit 2 treated as BLOCK — entire Bash/Write/Edit capability deadlocked. Required 2 full Claude Code session restarts.
- **Root cause:** Hook paths in `.claude/settings.json` were relative. Combined with cwd-leaking `cd`, they became unresolvable.
- **Classification:** Systemic — any bare `cd` call in any session would have hit it.
- **Fix applied during phase:** `.claude/settings.json` hook paths made absolute (`${CLAUDE_PROJECT_DIR}/scripts/hooks/...`); subshell `(cd foo && cmd)` mandate added to CLAUDE.md and frontend-agent.md.
- **Permanent:** Yes. Hook absolutization removes the catastrophic failure mode. Subshell discipline removes the surface.

### F3 — Edge Runtime crash from node:fs import in i18n.ts (01b-H2)
- **Symptom:** `npm run build` failed with `UnhandledSchemeError` because `middleware.ts` transitively imported `i18n.ts` which imported `node:fs/promises`.
- **Root cause:** i18n-agent.md had no constraint against Node.js built-ins in `i18n.ts`. The file had no context that it lives on Edge Runtime.
- **Classification:** Systemic — would hit any future i18n.ts change that added server-side logic.
- **Fix applied during phase:** Edge Runtime constraint added to i18n-agent.md; main-session override stripped offending imports.
- **Permanent:** Yes.

### F4 — Playwright CJS / import.meta.url crash (01b-H2)
- **Symptom:** i18n.spec.ts used `import.meta.url` (ESM pattern); Playwright CJS compilation left it undefined → `ReferenceError` at runtime.
- **Root cause:** Frontend-agent.md had no guidance on Playwright's CJS compilation target.
- **Classification:** Systemic — any test copied from an ESM example would hit this.
- **Fix applied during phase:** CJS constraint added to frontend-agent.md; main-session override switched to `process.cwd()`.
- **Permanent:** Yes.

### F5 — next-intl localeDetection defaulting to Accept-Language (01b-H2)
- **Symptom:** CI browsers defaulted to EN; root-redirect tests expected `/lv`; tests failed.
- **Root cause:** next-intl's default is `localeDetection: true`. No rule in any agent file or CLAUDE.md mandated the flag.
- **Classification:** Systemic — would affect any future middleware rewrite.
- **Fix applied during phase:** `localeDetection: false` mandate added to CLAUDE.md and i18n-agent.md; main-session override patched middleware.ts.
- **Permanent:** Yes.

### F6 — noUncheckedIndexedAccess TS errors in focus trap (01c-H2)
- **Symptom:** `Modal.tsx` focus trap used `focusable[0]` and `focusable[focusable.length - 1]` directly. `tsconfig.json` has `noUncheckedIndexedAccess: true`, making these `T | undefined`. Build failed. 2 main-session overrides.
- **Root cause:** Frontend-agent.md had no guidance about `noUncheckedIndexedAccess` being enabled, nor about the specific pattern required for indexed array access in focus traps.
- **Classification:** Systemic — any future component writing array indexing without optional chaining or bounds check will fail the same way.
- **Fix location:** `frontend-agent.md` — add rule. See "Amendments" section.
- **Fix applied now:** Yes.

### F7 — Node version lockfile mismatch causing CI red (01e)
- **Symptom:** 01e CI red on lockfile mismatch because CI jobs lacked `actions/setup-node@v4`, running different Node versions than the lockfile was generated with.
- **Root cause:** CI workflow did not pin Node. Fixed by 01f H2 (devops-agent added setup-node@v4 to 5 jobs).
- **Classification:** Systemic — would recur whenever the lockfile was regenerated.
- **Fix applied during phase:** setup-node@v4 Node 20 added to all frontend-touching CI jobs in 01f H2.
- **Permanent:** Yes.

### F8 — jest-dom matchers unusable in Vitest without setup file (01d, 7 overrides)
- **Symptom:** 01d-H1 frontend-agent produced layout component tests using `toBeInTheDocument()` and `toHaveAttribute()` from `@testing-library/jest-dom`. These are not built-in Vitest matchers. The agent ran out of context mid-fix; 7 main-session overrides replaced them with vanilla Vitest equivalents (`toBeTruthy()`, `getAttribute()`).
- **Root cause:** `vitest.config.ts` has no `setupFiles` entry wiring `@testing-library/jest-dom/vitest-matchers`. The package is installed (`frontend/package.json` has `@testing-library/jest-dom`) but not configured. Frontend-agent.md has no rule documenting the project's testing assertion convention.
- **Classification:** Systemic — recurred from 01c to 01d (same matchers). Would affect every new component test file dispatched to frontend-agent.
- **Two remedies available:**
  1. Wire jest-dom in `vitest.config.ts` `setupFiles` (DevOps Agent scope — requires handoff).
  2. Document the vanilla-assertions convention in frontend-agent.md so the agent doesn't use jest-dom matchers.
- **Decision:** Document the convention now (fix is immediate, zero overhead). If Phase 02 writes enough tests that jest-dom is clearly preferable, file a handoff to devops-agent to add `setupFiles`. Both remedies are mutually compatible.
- **Fix location:** `frontend-agent.md`. See "Amendments" section.
- **Fix applied now:** Yes.

### F9 — Simplify refactors generate multiple overrides per phase close (simplify cleanup)
- **Symptom:** Simplify cleanup at end of Phase 01 required 6 main-session scope-overrides to extract shared `navigation.ts` and `focus-trap.ts` utilities across 4 component files — all outside main_session's normal allow list.
- **Root cause:** Simplify findings that span multiple component files (cross-file deduplication) cannot be actioned by agents within their current dispatch context (the dispatch is already closed). They surface at phase close, requiring main-session overrides.
- **Classification:** Systemic but acceptable — this is the intended flow. CLAUDE.md already documents that simplify findings must be addressed before phase close, and the override mechanism exists for this purpose.
- **Verdict:** The override count (6) is high but the cause (cross-component deduplication) is inherently a phase-close activity. No process change needed. The existing "More than one override per sub-phase is a retrospective finding" clause correctly flags the intra-sub-phase overrides (F3/F4/F5/F6/F8) for retrospective review; phase-close simplify is a different regime.

---

## Amendments Applied

### 1. `frontend-agent.md` — noUncheckedIndexedAccess array indexing pattern

Added to the TypeScript section: when `noUncheckedIndexedAccess: true` is set (it is in `tsconfig.json`), direct array indexing `arr[i]` yields `T | undefined`. Pattern for focus traps and similar:
- Use `arr.at(0)` (returns `T | undefined`, then narrow) or explicit bounds check.
- Never directly call `.focus()` on an indexed element without a null guard.

Why: Phase 01c — 2 main-session overrides to fix Modal.tsx focus trap; same error class would affect any future component that indexes into arrays without bounds checks.

### 2. `frontend-agent.md` — Vitest assertion convention (no jest-dom matchers)

Added: Do not use `@testing-library/jest-dom` matchers (`toBeInTheDocument`, `toHaveAttribute`, `toHaveClass`, etc.) in Vitest unit tests unless `vitest.config.ts` has a `setupFiles` entry wiring them. As of Phase 01, there is no such entry. Use vanilla Vitest + DOM assertions instead:

| Instead of | Use |
|---|---|
| `expect(el).toBeInTheDocument()` | `expect(el).toBeTruthy()` |
| `expect(el).toHaveAttribute("x", "y")` | `expect(el.getAttribute("x")).toBe("y")` |
| `expect(el).toHaveClass("foo")` | `expect(el.classList.contains("foo")).toBe(true)` |

Why: Phase 01d — agent produced 7 test files using jest-dom matchers; none ran. 7 main-session overrides required. The package is installed but not wired into vitest.config.ts.

---

## Phase 02 Readiness

All Phase 01 friction items now have either a permanent fix or a documented convention. No blocking gaps remain for Phase 02.

**Watch for in Phase 02:**
- Backend components will use Python. The `noUncheckedIndexedAccess` class of issue has a Python analogue: `Optional` indexing on lists/dicts without narrowing. Backend-agent.md has no explicit guidance on this. If it surfaces, apply the same "document the pattern" fix.
- First use of `@testing-library/jest-dom` matchers in Vitest after the above convention is documented will be a signal that the convention is not visible enough. If it recurs once, add `setupFiles` to `vitest.config.ts` via devops-agent rather than documenting further.
- Phase 02 will introduce backend agents (database, backend). Verify that parallel dispatch works across different agent types before relying on it for critical-path handoffs.
