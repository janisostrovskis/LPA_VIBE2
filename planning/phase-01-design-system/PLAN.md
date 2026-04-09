# Phase 01: Design System & Layout Shell

## Objective

Ship the LPA design system and layout shell in code: all `--lpa-*` Tailwind tokens, font loading (Montserrat via `next/font/google` + fallback-only loading for Songer/Winterlady until the proprietary `.woff2` files are provided), six UI primitives (Button, Card, Input, Modal, Badge, Toast), four layout components (Header, Footer, MobileNav, LanguageSwitcher), `next-intl` wired into `[locale]/layout.tsx`, static placeholder pages for every public route in LV/EN/RU, and automated WCAG 2.2 AA verification via `@axe-core/playwright` backed by a CI gate. No backend work -- Phase 01 touches zero files under `backend/**`.

Phase 01 is the **first phase to ship real UI**. Phase 0 built the guardrails; Phase 01 proves they hold when the repo fills with actual application code.

## Prerequisites

- Phase 0 complete: all 9 sub-phases (00a-00i) landed green on master. COLA import enforcement, file-size limits, scope guard, handoff hygiene, simplify gate, parallel dispatch + background CI watch, and full empty COLA folder tree are all in place.
- Frontend scaffold (00c) exists: Next 15 + React 19 + TS strict + Tailwind 3.4 + ESLint flat + Vitest + Playwright configured; `frontend/src/app/layout.tsx`, `frontend/src/app/page.tsx`, `frontend/src/app/[locale]/layout.tsx`, `frontend/src/app/[locale]/page.tsx`, and test smoke files exist.
- `frontend/tailwind.config.ts` has 11 `lpa-*` color tokens, xs-xxxl spacing, md/lg/xl breakpoints, `card: 12px` radius, and `fontFamily` stubs for Songer / Montserrat / Winterlady.
- `frontend/src/app/globals.css` has 11 matching `--lpa-*` CSS variables.
- `frontend/src/components/`, `frontend/public/fonts/`, and `frontend/public/locales/` do **not** exist. `next-intl` is **not** installed.
- `docs/LPA_DESIGN_LANGUAGE.MD` and `docs/LPA_BUSINESS_CASE.MD` are the authoritative specifications for this phase.

## Deliverables

Per `planning/MASTER_PLAN.md` lines 268-283:

1. `frontend/tailwind.config.ts` with all `--lpa-*` tokens mapped
2. Font loading: Songer, Montserrat, Winterlady
3. UI primitives in `frontend/src/components/ui/`: Button, Card, Input, Modal, Badge, Toast
4. Layout components: Header, Footer, MobileNav, LanguageSwitcher
5. `frontend/src/app/[locale]/layout.tsx` with i18n routing via `next-intl`
6. Static placeholder pages for all public routes
7. WCAG 2.2 AA compliance verified on all interactive primitives

## Sub-phases

| Sub-phase | Scope | Owners | Status |
|-----------|-------|--------|--------|
| **01a** | Design token expansion + font loading infrastructure. Extend Tailwind with pill radius, card/card-hover shadows, typography scale (display/h1-h4/body-lg/body/caption), font weights. Load Montserrat via `next/font/google`. Set up `@font-face` fallback chain for Songer/Winterlady. Expand globals.css. Smoke-test on the existing `[locale]/page.tsx` hero. | frontend-agent (H1) | Not started |
| **01b** | `next-intl` infrastructure: install package, seed LV/EN/RU `common.json` message files, create `src/lib/i18n.ts` loader, add `src/middleware.ts` locale middleware, wire `NextIntlClientProvider` into `[locale]/layout.tsx`. | i18n-agent (H1) -> frontend-agent (H2) -- **sequential** | Not started |
| **01c** | UI primitives: Button, Card, Badge (H1) and Input, Modal, Toast (H2) with vitest unit tests covering render, keyboard interaction, and a11y attributes. First real test of **same-agent parallel dispatch** -- both H1 and H2 are frontend-agent with disjoint file sets. | frontend-agent x 2 -- **parallel** | Not started |
| **01d** | Layout shell: Header (logo, nav, LanguageSwitcher, mobile trigger), Footer (legal links, contact, copyright), MobileNav (full-screen drawer, focus trap), LanguageSwitcher (LV/EN/RU buttons wired to `next-intl`). Wire shell into `[locale]/layout.tsx`. | frontend-agent (H1) | Not started |
| **01e** | Placeholder pages for 12 public routes x 3 locales (36 URLs): about, join, trainings, directory, news, resources, verify, contact, legal/{privacy,terms,cookies}, plus home page upgrade. i18n-agent extends `common.json`; frontend-agent creates pages + e2e test. | i18n-agent (H1) -> frontend-agent (H2) -- **sequential** | Not started |
| **01f** | Accessibility verification: `@axe-core/playwright` e2e test visiting all 36 URLs asserting 0 critical/serious violations, plus CI `a11y-check` job with `hashFiles()` gating. Any violations found trigger component fixes. | frontend-agent (H1) || devops-agent (H2) -- **parallel** | Not started |

**Dependency chain:** 01a -> 01b -> 01c -> 01d -> 01e -> 01f. 01d depends on 01b (LanguageSwitcher uses `next-intl` hooks) and 01c (Header uses `Button`, MobileNav may reuse `Modal`). 01e depends on 01d (pages use the layout shell) and 01b (pages read translations). 01f depends on 01e (axe needs real pages to audit).

**First real use of same-agent parallel dispatch is 01c.** Phase 0 validated cross-agent parallel in 00g (database-agent || backend-agent). Phase 01 validates same-agent parallel; the observed behavior will be recorded in `RETROSPECTIVE.md`.

## Agent Assignments

| Path / deliverable | Owner | Rationale |
|--------------------|-------|-----------|
| `planning/phase-01-design-system/PLAN.md` (this file) | main-session | `planning/**` is main-session scope per `.claude/scope.yaml`. |
| `planning/phase-01-design-system/HANDOFF_LOG.md` | all agents (via `planning/**/HANDOFF_LOG.md` carve-out) | Each handoff appends its own entry. |
| `frontend/tailwind.config.ts`, `frontend/src/app/**`, `frontend/src/components/**`, `frontend/public/fonts/**` | frontend-agent | Design system + component library + pages. |
| `frontend/src/lib/i18n.ts`, `frontend/src/lib/i18n/**`, `frontend/public/locales/**` | i18n-agent | Translation files + i18n loader per scope.yaml explicit assignment. |
| `frontend/package.json`, `frontend/package-lock.json` | frontend-agent | Both frontend-agent and devops-agent have this in allow list; Phase 01 assigns to frontend-agent since all new deps are frontend-local (`next-intl`, `@axe-core/playwright`, potentially `@radix-ui/react-dialog`). |
| `frontend/src/middleware.ts` | frontend-agent (via `frontend/src/**`) | Next.js locale middleware; not i18n-agent because middleware.ts is not explicitly in i18n-agent scope. |
| `.github/workflows/ci.yml` | devops-agent | CI configuration. |
| `frontend/tests/e2e/**` | frontend-agent | E2E test files. |

## Scope ownership resolutions

Ambiguous paths and the explicit Phase 01 assignment:

| Path | Overlap | Phase 01 owner |
|------|---------|----------------|
| `frontend/src/lib/i18n.ts` | i18n-agent + frontend-agent (via `src/**`) | **i18n-agent** |
| `frontend/src/lib/i18n/**` | i18n-agent + frontend-agent | **i18n-agent** |
| `frontend/package.json`, `frontend/package-lock.json` | frontend-agent + devops-agent | **frontend-agent** |
| `frontend/tailwind.config.ts` | frontend-agent + devops-agent (via `*.config.*`) | **frontend-agent** |
| `frontend/src/app/[locale]/layout.tsx` | frontend-agent only | frontend-agent |
| `frontend/public/locales/**` | i18n-agent only | i18n-agent |
| `frontend/public/fonts/**` | frontend-agent only (via `public/**`) | frontend-agent |

## Acceptance Criteria

Business case `docs/LPA_BUSINESS_CASE.MD` sections:
- **3.9 Multilingual (LV/EN/RU):** language switcher present across site, user preference remembered, pages + emails in LV/EN/RU, URLs reflect language.
- **3.14 Accessibility & Inclusivity:** WCAG 2.2 AA conformance -- color contrast, keyboard navigation, screen-reader labeling, error messaging, focus states, plain-language content on Join/Trainings/Directory pages.
- **3.17 Brand & UX Guidelines:** clean accessible visual style with limited palette, consistent components (buttons, forms, cards, badges), clear CTAs, professional/warm/trustworthy tone.

## Phase 1 testing gate

Runs at sub-phase **01f** close before the phase is declared complete. Gate items:

1. **Design tokens match the language doc.** Manual comparison of `frontend/tailwind.config.ts` and `frontend/src/app/globals.css` against tables in `docs/LPA_DESIGN_LANGUAGE.MD` -- every color, radius, shadow, fontSize, breakpoint present.
2. **Fonts render.** Montserrat loads via next/font (verified by `npm run build`). Songer and Winterlady fall back gracefully if `.woff2` files not yet provided; `frontend/public/fonts/README.md` visible and accurate. **Gate waiver acceptable** if real fonts not yet dropped -- re-run visual QA when they arrive.
3. **Keyboard nav works.** Tab from Header through content to Footer with visible focus at every stop. MobileNav opens/closes via keyboard.
4. **Language switcher changes URL.** On `/lv/about`, clicking EN navigates to `/en/about`. Verified in Playwright.
5. **All 12 routes x 3 locales render.** `frontend/tests/e2e/routes.spec.ts` green.
6. **WCAG AA primitives pass axe.** `frontend/tests/e2e/a11y.spec.ts` green (0 critical/serious violations).
7. **Mobile nav at 375px.** Playwright runs with `viewport: { width: 375, height: 812 }` and drawer still works.
8. **CI fully green.** All existing 9 jobs plus new `a11y-check` = 10 jobs pass on master.
9. **Handoff log valid.** `python scripts/check_handoff_log.py` -> exit 0; every source-touching entry dated 2026-04-09+ has a simplify receipt under `simplify-receipts/`.
10. **Sub-phases table updated.** All 6 rows flipped to **Complete**.
11. **TESTING_GATE.md written** per rulebook section B.4 (unit, integration, E2E, manual verification, simplify review, security review; any waivers justified).
12. **SECURITY_REVIEW.md written** per rulebook section B.3 (COLA, secrets, auth/authz, data protection, error handling -- Phase 01 is UI-only so most sections N/A; CSP headers, XSS, and `npm audit` apply).
13. **RETROSPECTIVE.md written** with findings (same-agent parallel dispatch behavior, `next-intl` version selection, font-loading surprises, any axe violation fixes).

Post-gate: **Phase 2 (Accounts & Authentication) unblocks.**

## Phase-level risks

| # | Risk | Mitigation |
|---|------|------------|
| R1.A | Songer and Winterlady are proprietary fonts not in the repo. Visual parity depends on the user providing `.woff2` files. | 01a ships fallback-only loading via `@font-face` + `font-display: swap` so missing files don't break builds. Gate item #2 is waivable. Visual QA for Phase 2 must re-verify once fonts arrive. |
| R1.B | `next-intl` v3+ API may shift under Next 15. | 01b H2's Rule 3 runs `npm run build` -- build-time validation catches version drift immediately. If broken, downgrade to the last working v3 minor and document. |
| R1.C | Axe-core may flag violations in 01c/01d components, creating fix-up churn in 01f. | Time-box fixes to one session. Unresolvable violations become retrospective findings with justified waivers in TESTING_GATE.md. |
| R1.D | Scope ambiguity: `frontend/src/lib/i18n.ts`, `frontend/package.json`, `frontend/tailwind.config.ts` are in multiple agents' allow lists. | Plan explicitly assigns owners (see scope ownership resolutions table). Each handoff brief names the owner. |
| R1.E | Same-agent parallel dispatch (01c H1 + H2, both frontend-agent) is untested. First attempt may serialize. | Accept wall-clock cost on first attempt. File a retrospective note on observed behavior -- no functional impact if serialized. Phase 0 validated cross-agent parallel (00g); Phase 01 validates same-agent. |
| R1.F | Frontend-design skill is mandatory per Rule 1 but not hook-enforced; agents may skip. | Include explicit "Rule 1: invoke `frontend-design` skill BEFORE editing any UI file" in every handoff brief. Main session spot-checks the agent's reply for skill invocation output. |
| R1.G | 01e creates 12 pages x 3 locales = 36 routes; TypeScript compile time may grow. | Accept for Phase 01. If `npm run build` exceeds 60s in 01e H2 verification, split 01e into `public` + `legal` handoffs. |
| R1.H | `next-intl` may require a config file at a specific path (e.g., `src/i18n/request.ts`) not explicitly in i18n-agent scope. | If required, frontend-agent creates the next-intl root config file under `frontend/src/i18n/**` (in frontend-agent scope via `src/**`) and imports helpers from i18n-agent's `src/lib/i18n.ts`. Document decision in 01b H2's receipt. |
| R1.I | Modal focus-trap may require a runtime dep like `@radix-ui/react-dialog` or `focus-trap-react`. Adds a dep and package-lock churn. | 01c H2 decides at implementation time: hand-rolled first, fall back to Radix if fragile. Document in receipt. If Radix is adopted, add to 01c H2's `package.json` edits. |
| R1.J | Legal page content (Privacy/Terms/Cookies) is placeholder only -- real legal text is a lawyer job. | 01e ships placeholder text with `TODO: replace with legal-reviewed text` comments. Legal content delivery tracked outside Phase 01. |

## Out of scope (phase-level)

- **Real translation content.** 01b and 01e seed minimal keys only. Full translations (marketing copy, legal text) are later work once business content exists.
- **Authenticated layout.** Phase 01 ships the public shell only. `(auth)/**` routes are Phase 2.
- **Admin layout.** `(admin)/**` routes are Phase 8.
- **Real content on public pages.** 01e ships placeholders only. Content population is Phase 10.
- **Songer/Winterlady `.woff2` files.** Deferred to user sourcing; plan is robust to their absence.
- **Backend work.** Phase 01 touches zero files under `backend/**`.
- **Payment provider selection.** Phase 3.
- **Dark mode.** Not specified in design language.
- **Error boundary UI / 404 page / 500 page.** Defer unless axe in 01f forces them in.
- **CMS integration.** Future phase.
- **Email template design.** Phase 9.

---

## Sub-phase 01a -- Design tokens + font loading

**Goal:** Expand Tailwind config to the full design-language spec, load Montserrat via `next/font/google`, set up fallback loading for Songer/Winterlady, expand globals.css with typography utilities, and smoke-test the new tokens on the existing `[locale]/page.tsx` hero.

**Owner:** frontend-agent (single handoff H1). Pure visual-system expansion -- no i18n or routing work.

### 01a Deliverables (~7 files)

1. `frontend/tailwind.config.ts` -- extend:
   - `borderRadius`: add `pill: "9999px"` (keep existing `card: "12px"`)
   - `boxShadow`: add `card: "0 4px 12px rgba(0,0,0,0.06)"` and `card-hover: "0 8px 24px rgba(0,0,0,0.1)"`
   - `fontSize`: add `display` (64px / 1.1), `h1` (48px / 1.15), `h2` (36px / 1.2), `h3` (28px / 1.25), `h4` (22px / 1.3), `body-lg` (18px / 1.6), `body` (16px / 1.6), `caption` (14px / 1.4)
   - `fontFamily`: ensure Songer/Montserrat/Winterlady stacks reference their CSS variables and include proper fallback chains
   - `screens`: optionally add `sm: "480px"` if the design language spec implies a mobile-specific breakpoint
2. `frontend/src/app/layout.tsx` -- import `Montserrat` from `next/font/google` with weights 400/500/700, expose as CSS var `--font-montserrat`, apply class on `<body>` (not `<html>` -- next/font best practice)
3. `frontend/src/app/globals.css` -- add:
   - `@font-face` declarations for `Songer` and `Winterlady` pointing to `/fonts/Songer.woff2` and `/fonts/Winterlady.woff2` with `font-display: swap`
   - Base body rule: `font-family: var(--font-montserrat), system-ui, sans-serif; font-size: 16px; line-height: 1.6;`
   - `@media (prefers-reduced-motion: reduce)` rule that disables transitions/animations
   - Ensure existing `:root { --lpa-* }` block stays intact
4. `frontend/public/fonts/README.md` -- document that `Songer.woff2` and `Winterlady.woff2` must be dropped in this directory by the user; until then the browser falls back to `system-ui, serif` / `cursive`
5. `frontend/public/fonts/.gitkeep` -- ensure the empty directory is tracked by git
6. `frontend/src/app/[locale]/page.tsx` -- update hero to use `className="text-display font-sans"` (or similar) as a sanity check that tokens resolve end-to-end; do not change copy
7. (optional) trivial vitest assertion if the existing smoke test needs adjusting

### 01a Handoff -- H1 (frontend-agent)

- **Preamble:** the mandatory "Execute the following. This is not a planning task..." sentence per CLAUDE.md "Subagent dispatch preamble".
- **Rule 1:** invoke `frontend-design` skill **before** editing any file under `frontend/src/app/**` or `frontend/tailwind.config.ts`.
- **Rule 2:** invoke `simplify` on changed files -> receipt `planning/phase-01-design-system/simplify-receipts/01a-H1-frontend-agent.md`.
- **Rule 3 verification** (terminal):
  - `cd frontend && npm run build` -> exit 0
  - `cd frontend && npx vitest run` -> exit 0
  - `cd frontend && npx playwright test` -> exit 0 (existing smoke test still passes)
  - `python scripts/check_file_size.py` -> exit 0
  - `pre-commit run --files <changed>` -> exit 0
- **Timing:** main session records dispatch-start, dispatch-end, commit, ci-green/red events via `scripts/log_handoff_timing.py --phase 01a --handoff H1`.

### 01a Testing Requirements

1. `cd frontend && npm run build` exits 0.
2. `cd frontend && npx vitest run` exits 0.
3. `cd frontend && npx playwright test` exits 0 (existing `smoke.spec.ts`).
4. `/lv` renders with the new typography utilities. Manual visual check: hero heading uses the `display` size; body text uses Montserrat.
5. `frontend/public/fonts/README.md` present and explains the pending font drop.
6. `python scripts/check_file_size.py` exits 0.
7. `python scripts/check_cola_imports.py` exits 0.
8. `python scripts/check_handoff_log.py` exits 0 (new 01a H1 entry valid).
9. `pre-commit run --all-files` passes.
10. CI green on master (all existing 9 jobs).

### 01a Risks (additions)

| # | Risk | Mitigation |
|---|------|------------|
| R1.1 | Songer/Winterlady `.woff2` files are proprietary and not in the repo; `@font-face` with missing files will produce 404s in the browser console. | `font-display: swap` ensures the browser uses the fallback immediately without blocking render. Console noise is accepted. `public/fonts/README.md` explains. |
| R1.2 | `next/font/google` requires network access at build time. | Next.js caches downloaded fonts; first CI run downloads, subsequent runs hit cache. Acceptable. |

---

## Sub-phase 01b -- i18n infrastructure (next-intl)

**Goal:** Install `next-intl`, seed LV/EN/RU `common.json` message files, create the i18n loader, add locale middleware, and wire `NextIntlClientProvider` into `[locale]/layout.tsx` so URL-prefix routing resolves real translations.

**Owners:** i18n-agent (H1) -> frontend-agent (H2). **Sequential** -- H2's `middleware.ts` and `[locale]/layout.tsx` import from H1's `src/lib/i18n.ts`; pre-commit type-check in H2 would fail if the import target doesn't exist yet.

### 01b Deliverables (~9 files)

**H1 -- i18n-agent (4 files):**

- `frontend/src/lib/i18n.ts` -- exports `locales = ["lv","en","ru"] as const`, `defaultLocale = "lv"` (const), `type Locale = typeof locales[number]`, and a `getMessages(locale: Locale)` async loader that imports JSON via dynamic import (`import(\`../../public/locales/\${locale}/common.json\`)` or reads via `fs` -- depends on next-intl v3 idioms).
- `frontend/public/locales/lv/common.json` -- seed ~20 keys covering header nav, footer, common UI. Keys must be consistent across all three locales. Example structure:
  ```json
  {
    "site": { "name": "<LV site name>" },
    "nav": { "home": "<LV home>", "about": "<LV about>", "join": "<LV join>", "trainings": "<LV trainings>", "directory": "<LV directory>", "news": "<LV news>", "resources": "<LV resources>", "verify": "<LV verify>", "contact": "<LV contact>" },
    "footer": {
      "legal": { "privacy": "<LV privacy>", "terms": "<LV terms>", "cookies": "<LV cookies>" },
      "copyright": "(c) 2026 LPA"
    },
    "language": { "lv": "<LV>", "en": "English", "ru": "<RU>" },
    "common": { "loading": "<LV loading>", "error": "<LV error>", "closeMenu": "<LV close menu>" }
  }
  ```
- `frontend/public/locales/en/common.json` -- same keys, English values
- `frontend/public/locales/ru/common.json` -- same keys, Russian values

**H2 -- frontend-agent (5 files):**

- `frontend/package.json` -- add `"next-intl": "<pinned>"`. **Pin to the current compatible version** via `npm view next-intl version` -- **no invented versions**.
- `frontend/package-lock.json` -- regenerated by `npm install`
- `frontend/src/middleware.ts` -- `createMiddleware` from `next-intl/middleware`, matcher `"/((?!api|_next|.*\\..*).*)"`, `locales` and `defaultLocale` imported from `@/lib/i18n` (or relative path)
- `frontend/src/app/[locale]/layout.tsx` -- wrap children in `<NextIntlClientProvider messages={await getMessages(locale)}>`. Replace the hand-rolled `generateStaticParams` if next-intl provides its own.
- `frontend/src/app/layout.tsx` -- ensure bare passthrough (next-intl routes through `[locale]/layout.tsx`). Strip redundant `<html lang="lv">` if next-intl requires setting the `lang` attribute dynamically.
- `frontend/src/app/page.tsx` -- keep `redirect("/lv")` or let next-intl middleware handle the root redirect, whichever works with the installed version.
- `frontend/tests/e2e/i18n.spec.ts` -- new e2e test: visits `/lv`, `/en`, `/ru`, asserts each renders its localized site name.

### 01b Handoffs

**H1 -- i18n-agent (first):**
- Preamble.
- Rule 2: `simplify` -> receipt `01b-H1-i18n-agent.md` (likely `waived -- seed JSON + thin loader wrapper, no logic`).
- Rule 3 verification:
  - `cd frontend && npx tsc --noEmit` -> exit 0 (i18n.ts compiles)
  - `python -c "import json; [json.load(open(f'frontend/public/locales/{l}/common.json')) for l in ('lv','en','ru')]"` -> exit 0
  - Key-parity check: same keys present in all three files
  - `pre-commit run --files <changed>` -> exit 0

**H2 -- frontend-agent (after H1 commits):**
- Preamble.
- Rule 1: `frontend-design` before touching `[locale]/layout.tsx`.
- Rule 2: `simplify` -> receipt `01b-H2-frontend-agent.md`.
- Rule 3 verification:
  - `cd frontend && npm install` -> exit 0 (next-intl resolves)
  - `cd frontend && npm run build` -> exit 0
  - `cd frontend && npx vitest run` -> exit 0
  - `cd frontend && npx playwright test tests/e2e/smoke.spec.ts tests/e2e/i18n.spec.ts` -> exit 0
  - `pre-commit run --files <changed>` -> exit 0

### 01b Testing Requirements (additions)

11. `frontend/src/lib/i18n.ts` type-checks clean.
12. All three `common.json` files parse and have identical key trees.
13. `cd frontend && npm install` resolves `next-intl`.
14. `cd frontend && npm run build` passes with `next-intl` wired into the layout.
15. `/` redirects to `/lv`.
16. `/lv`, `/en`, `/ru` all render with localized site names.
17. `i18n.spec.ts` e2e test green.
18. CI green on both commits.

### 01b Risks (additions)

| # | Risk | Mitigation |
|---|------|------------|
| R1.3 | `next-intl` v3 requires a specific Next version; Next 15 compatibility may have gaps. | H2 Rule 3 runs `npm run build` -- incompatibility surfaces immediately. If broken, pin an older working v3 minor. |
| R1.4 | `next-intl` v3 recommends config at `src/i18n/request.ts` not `src/lib/i18n.ts`. | If required, frontend-agent creates `src/i18n/request.ts` (in its `src/**` scope) and imports helpers from i18n-agent's `src/lib/i18n.ts`. Document in receipt. |
| R1.5 | Middleware placement -- `src/middleware.ts` vs `middleware.ts` root -- depends on `src/` layout convention. | We use `src/` layout, so `src/middleware.ts` is correct. Verify via `curl localhost:3000/` redirect behavior. |

---

## Sub-phase 01c -- UI primitives

**Goal:** Build the 6 foundational UI components per design-language spec. Every component uses only `lpa-*` Tailwind tokens, has a visible focus state, has vitest unit tests, and ships TS-strict-clean with no `any`.

**Owner:** frontend-agent x 2 -- **parallel dispatch** in a single message.

**Why parallel is viable:** both handoffs are frontend-agent, touch disjoint file sets, have no runtime imports between them, and each can independently pass `npm run build` / `vitest run` / `pre-commit run --files`. The Agent tool spawns a new agent instance per call. This is the **first test of same-agent parallel dispatch** -- record observed behavior in RETROSPECTIVE.md.

### 01c Deliverables (~12 files)

**H1 -- Static primitives (Button, Card, Badge):**

- `frontend/src/components/ui/Button.tsx`:
  - Variants: `primary` (sage fill, pill radius, uppercase, letter-spacing 0.08em, Montserrat 500 15px), `secondary` (outlined 1.5px ink border, transparent bg), `text` (no border, underline on hover, color transitions to sage)
  - Sizes: `sm` | `md` | `lg`
  - Props: `variant`, `size`, `disabled`, `loading`, `type`, `onClick`, `children`
  - Focus-visible: 2px mint ring with 2px offset
  - Active: `translateY(0)`, no shadow
  - Hover: `translateY(-2px)`
- `frontend/src/components/ui/Card.tsx`:
  - Base: border-light 1px, radius 12px (`rounded-card`), shadow `card`, padding 24px
  - Optional `hover` prop: adds `-translate-y-0.5` lift + `hover:shadow-card-hover`, `transition-all duration-300 ease-out`
- `frontend/src/components/ui/Badge.tsx`:
  - Variants: `neutral` | `sage` | `mint` | `taupe`
  - Pill radius, padding `px-2.5 py-1`, caption-size font, Montserrat 500
- `frontend/src/components/ui/__tests__/Button.test.tsx` -- render per variant, click handler fires, disabled prevents click, focus-visible ring class applied
- `frontend/src/components/ui/__tests__/Card.test.tsx` -- render with and without `hover` prop
- `frontend/src/components/ui/__tests__/Badge.test.tsx` -- render per variant

**H2 -- Interactive primitives (Input, Modal, Toast):**

- `frontend/src/components/ui/Input.tsx`:
  - Label associated via `htmlFor`/`id`; optional `hint`, `error` props
  - Error state: red border `#b64949`, error message linked via `aria-describedby`
  - 4px radius (not pill), Montserrat 16px, placeholder color tertiary
  - Focus-visible: sage border + `box-shadow: 0 0 0 3px rgba(156,175,136,0.16)`
  - Props: `label`, `id`, `value`, `onChange`, `placeholder`, `type`, `error`, `hint`, `disabled`, `required`
- `frontend/src/components/ui/Modal.tsx`:
  - `<dialog>` element; focus trap (first focusable on open, restore on close)
  - ESC key closes; click-outside-to-close (overlay click)
  - `aria-modal="true"`, `role="dialog"`, `aria-labelledby={titleId}`
  - Portal-rendered to `document.body`
  - **Decision point:** hand-rolled or Radix. Default: hand-rolled (no new dep); fall back to `@radix-ui/react-dialog` if focus-trap proves fragile. Decision documented in 01c H2 simplify receipt; if Radix is adopted, add to `frontend/package.json` edits in the same handoff.
- `frontend/src/components/ui/Toast.tsx`:
  - `role="status"` for `info`/`success`, `role="alert"` for `error`
  - Auto-dismiss after configurable timeout (default 5000ms)
  - Positioned `fixed top-4 right-4`, appropriate `z-index`
  - Variants: `success` (sage), `error` (#b64949), `info` (mint)
- `frontend/src/components/ui/__tests__/Input.test.tsx` -- label/input association, error state renders + `aria-describedby` wiring, disabled prevents input
- `frontend/src/components/ui/__tests__/Modal.test.tsx` -- opens, ESC closes, click outside closes, focus trap holds, focus restores on close (uses `@testing-library/user-event`)
- `frontend/src/components/ui/__tests__/Toast.test.tsx` -- renders, auto-dismisses after timeout, variant classes applied

### 01c Pre-flight protocol

Before dispatching both Agent calls in a single message:

1. `python scripts/preflight_dispatch.py --agent frontend-agent --files <H1 file list>` -> exit 0
2. `python scripts/preflight_dispatch.py --agent frontend-agent --files <H2 file list>` -> exit 0
3. Verify union of H1 + H2 file sets has no duplicates (by construction, none).
4. Record `log_handoff_timing.py --phase 01c --handoff H1 --event dispatch-start`, same for H2.
5. Dispatch both `Agent(subagent_type="frontend-agent", ...)` calls in one message.

### 01c Handoffs

**H1 -- frontend-agent (Button / Card / Badge):**
- Preamble.
- Rule 1: `frontend-design` before any component file.
- Rule 2: `simplify` -> receipt `01c-H1-frontend-agent.md`.
- Rule 3: `cd frontend && npx vitest run src/components/ui/__tests__/Button.test.tsx src/components/ui/__tests__/Card.test.tsx src/components/ui/__tests__/Badge.test.tsx` -> exit 0; `cd frontend && npm run build` -> exit 0; `pre-commit run --files <changed>` -> exit 0.

**H2 -- frontend-agent (Input / Modal / Toast):**
- Preamble.
- Rule 1: `frontend-design`.
- Rule 2: `simplify` -> receipt `01c-H2-frontend-agent.md`.
- Rule 3: analogous to H1, targeting H2's test files.

**Post-handoff (main session):**
- Both return independently; stage + commit each in separate commits (order doesn't matter since no overlap).
- Background `gh run watch --exit-status` per commit.
- Record `commit` and `ci-green`/`ci-red` timing events per handoff.
- Final blocking watch at sub-phase close.

### 01c Testing Requirements (additions)

19. All 6 component test files pass.
20. `cd frontend && npm run build` exits 0 with new components.
21. Each component exports a named type for its props.
22. TypeScript strict mode clean -- no `any`, no `@ts-ignore`.
23. No ad-hoc hex codes outside `#b64949` (design-language-mandated error color).
24. Focus states verified in Playwright snapshot tests or manual check.
25. CI green on both H1 and H2 commits.

### 01c Risks (additions)

| # | Risk | Mitigation |
|---|------|------------|
| R1.6 | Same-agent parallel dispatch (both H1 and H2 are frontend-agent) may be serialized by the harness. | Accept wall-clock cost on first attempt. Record observed behavior in RETROSPECTIVE.md. No functional impact if serialized. |
| R1.7 | Modal focus-trap + ESC handling is non-trivial; hand-rolled may have edge cases. | If fragile after one iteration, adopt `@radix-ui/react-dialog` in the same handoff. Document decision in receipt. |
| R1.8 | Component tests may not catch visual regressions. | Accept for Phase 01 -- visual regression testing is future-phase work. |

---

## Sub-phase 01d -- Layout components

**Goal:** Build the shell that wraps every page -- Header with nav + LanguageSwitcher, Footer with legal links, MobileNav drawer, LanguageSwitcher component -- and wire the shell into `[locale]/layout.tsx` so all pages automatically get it. Header and MobileNav share state (menu open/close), so they ship in one handoff.

**Owner:** frontend-agent (single handoff H1).

### 01d Deliverables (~9 files)

- `frontend/src/components/layout/Header.tsx`:
  - Sticky 80-96px, bg `rgba(255,255,255,0.98)`, scroll-shadow behavior (add `shadow-[0_2px_8px_rgba(0,0,0,0.04)]` when scrolled)
  - Logo (placeholder SVG or styled text "LPA" until real asset is provided)
  - Desktop nav: home/about/join/trainings/directory/news/resources/verify/contact -- uppercase, Montserrat 14px 500, letter-spacing 0.08em; hover -> sage; active -> sage + bottom border
  - `LanguageSwitcher` rendered in the header bar
  - Mobile menu trigger (hamburger button) -- visible only below `md` breakpoint; toggles `MobileNav` state via a `useState` hook or URL query param
- `frontend/src/components/layout/Footer.tsx`:
  - `canvas-soft` background, padding `py-12 px-6 md:px-10`
  - Columns: LPA info (name + one-line description), legal (Privacy / Terms / Cookies linking to 01e routes), contact info, alternate `LanguageSwitcher`
  - Copyright line at bottom
- `frontend/src/components/layout/MobileNav.tsx`:
  - Full-screen overlay (or slide drawer); uses the `Modal` primitive from 01c or a custom pattern
  - Stacked nav links, 32px apart, min 48px tap targets
  - Focus trap (reusing Modal's if viable)
  - Closes on link click (navigation should dismiss the menu)
- `frontend/src/components/layout/LanguageSwitcher.tsx`:
  - Renders three buttons (LV/EN/RU) via `Button` primitive (`text` variant) or custom styling
  - Active locale marked (bold + sage color)
  - On click, uses `useRouter` + `usePathname` from `next/navigation` + `next-intl`'s routing helper to replace the locale segment in the current path
- `frontend/src/components/layout/__tests__/Header.test.tsx` -- renders all nav links from seeded `common.json`, mobile trigger toggles drawer, active nav item highlighted
- `frontend/src/components/layout/__tests__/Footer.test.tsx` -- renders legal links with correct hrefs
- `frontend/src/components/layout/__tests__/MobileNav.test.tsx` -- opens/closes, focus trap, ESC closes, link click dismisses
- `frontend/src/components/layout/__tests__/LanguageSwitcher.test.tsx` -- renders three language options, clicking triggers locale change (mock `next/navigation` router)
- `frontend/src/app/[locale]/layout.tsx` -- modify to render `<Header /><main>{children}</main><Footer />` wrapping the existing `NextIntlClientProvider` content

### 01d Handoff -- H1 (frontend-agent)

- Preamble.
- Rule 1: `frontend-design` before any layout component or `[locale]/layout.tsx`.
- Rule 2: `simplify` -> receipt `01d-H1-frontend-agent.md`.
- Rule 3 verification:
  - `cd frontend && npx vitest run src/components/layout/` -> exit 0
  - `cd frontend && npm run build` -> exit 0
  - `cd frontend && npx playwright test tests/e2e/smoke.spec.ts tests/e2e/i18n.spec.ts` -> exit 0
  - `pre-commit run --files <changed>` -> exit 0

### 01d Testing Requirements (additions)

26. Header renders nav links across `/lv`, `/en`, `/ru` with correct localized labels.
27. MobileNav opens/closes keyboard-accessibly at 375px viewport.
28. LanguageSwitcher changes URL prefix on click (verified in Playwright).
29. Footer renders legal links (they point at routes that don't exist yet -- 404 expected until 01e).
30. `npm run build` exits 0.
31. All layout component tests pass.
32. CI green.

### 01d Risks (additions)

| # | Risk | Mitigation |
|---|------|------------|
| R1.9 | Footer links to `/legal/privacy` etc. that don't exist yet. | Acceptable for one sub-phase. e2e test asserts links render, not that they resolve. 01e creates destinations. |
| R1.10 | MobileNav as `Modal` subclass may conflict with the generic Modal's behavior (e.g., Modal closes on navigation but a drawer menu should persist until explicit close). | MobileNav implements its own close-on-link-click behavior rather than relying on Modal defaults. Document design decision in simplify receipt. |

---

## Sub-phase 01e -- Placeholder pages for 12 public routes

**Goal:** Create static placeholder pages for all public routes so the layout shell has real destinations. Each page uses the layout from 01d, primitives from 01c, and translations from 01b.

**Owners:** i18n-agent (H1) -> frontend-agent (H2). **Sequential** -- H2 pages read translations H1 adds.

### 01e Deliverables (~16 files)

**H1 -- i18n-agent (3 files):**

Extend `frontend/public/locales/{lv,en,ru}/common.json` with ~36 new page content keys (12 pages x ~3 keys each):

```
page.home.title, page.home.subtitle, page.home.cta
page.about.title, page.about.intro
page.join.title, page.join.intro
page.trainings.title, page.trainings.intro
page.directory.title, page.directory.intro
page.news.title, page.news.intro
page.resources.title, page.resources.intro
page.verify.title, page.verify.intro
page.contact.title, page.contact.intro
page.legal.privacy.title, page.legal.privacy.intro
page.legal.terms.title, page.legal.terms.intro
page.legal.cookies.title, page.legal.cookies.intro
```

All three locale files must receive the same keys. Content is placeholder text marked with `TODO: replace with real content` where appropriate (especially legal pages).

**H2 -- frontend-agent (13 files):**

- `frontend/src/app/[locale]/(public)/about/page.tsx`
- `frontend/src/app/[locale]/(public)/join/page.tsx`
- `frontend/src/app/[locale]/(public)/trainings/page.tsx`
- `frontend/src/app/[locale]/(public)/directory/page.tsx`
- `frontend/src/app/[locale]/(public)/news/page.tsx`
- `frontend/src/app/[locale]/(public)/resources/page.tsx`
- `frontend/src/app/[locale]/(public)/verify/page.tsx`
- `frontend/src/app/[locale]/(public)/contact/page.tsx`
- `frontend/src/app/[locale]/(public)/legal/privacy/page.tsx`
- `frontend/src/app/[locale]/(public)/legal/terms/page.tsx`
- `frontend/src/app/[locale]/(public)/legal/cookies/page.tsx`
- `frontend/src/app/[locale]/page.tsx` -- upgrade existing hero to the proper home page (title/subtitle from `page.home.*`, primary CTA Button linking to `/[locale]/join`)
- `frontend/tests/e2e/routes.spec.ts` -- Playwright test parametrized over 12 routes x 3 locales (36 cases), asserts HTTP 200 and the expected `<h1>` text from the translation file

Each page is a thin React component: heading from `useTranslations()`, intro paragraph, possibly a Card or Button from 01c. Legal pages may have a `<h2>Coming soon</h2>` block and a TODO comment.

No route-group layout (`(public)/layout.tsx`) unless a concrete need emerges -- `[locale]/layout.tsx` from 01d already wraps header/footer.

### 01e Handoffs

**H1 -- i18n-agent:**
- Preamble.
- Rule 2: `simplify` -> receipt `01e-H1-i18n-agent.md` (likely `waived -- translation content only`).
- Rule 3: JSON syntax + key parity across three locales; `pre-commit run --files <changed>` -> exit 0.

**H2 -- frontend-agent (after H1 commits):**
- Preamble.
- Rule 1: `frontend-design` before any page file.
- Rule 2: `simplify` -> receipt `01e-H2-frontend-agent.md`.
- Rule 3:
  - `cd frontend && npm run build` -> exit 0
  - `cd frontend && npx playwright test tests/e2e/routes.spec.ts` -> exit 0 (all 36 routes return 200)
  - `cd frontend && npx vitest run` -> exit 0
  - `pre-commit run --files <changed>` -> exit 0

### 01e Testing Requirements (additions)

33. All three `common.json` files have identical page-key trees.
34. `cd frontend && npm run build` passes with 12 new pages.
35. `routes.spec.ts` asserts 36 routes return 200 and each `<h1>` matches the translated title.
36. Footer legal links from 01d now resolve.
37. Home page shows new hero with CTA button linking to `/[locale]/join`.
38. `npx vitest run` passes.
39. CI green on both commits.

### 01e Risks (additions)

| # | Risk | Mitigation |
|---|------|------------|
| R1.11 | 36 URL assertions bloat the e2e test runtime. | Use `test.describe.each` or a loop to stay DRY. Accept runtime cost. |
| R1.12 | `next-intl` may throw at runtime on missing keys even though type-check passes. | H2 Rule 3 includes `npm run build` which exercises the runtime. If missing, extend H1's JSON. |
| R1.13 | 12 pages x 3 locales = 36 build outputs; TS compile time may grow. | Accept for Phase 01. If `npm run build` exceeds 60s, split 01e into `public` + `legal` handoffs. |

---

## Sub-phase 01f -- Accessibility verification

**Goal:** Confirm WCAG 2.2 AA compliance across the design system via automated axe-core checks. Fix any critical/serious violations found. Install a CI gate that blocks regressions.

**Owners:** frontend-agent (H1) || devops-agent (H2). **Parallel dispatch** -- zero file overlap; H2 writes the CI job ahead of time with `if: hashFiles(...)` gating so it activates automatically once H1's test file exists.

### 01f Deliverables (~4 files + any component fixes)

**H1 -- frontend-agent:**

- `frontend/package.json` -- add `"@axe-core/playwright": "<pinned>"` via `npm view @axe-core/playwright version`
- `frontend/package-lock.json` -- regenerated
- `frontend/tests/e2e/a11y.spec.ts` -- Playwright test that:
  - Loads each of 12 routes x 3 locales (36 URLs)
  - `await page.waitForLoadState("networkidle")` before running axe to avoid async-render flakiness
  - Runs `await new AxeBuilder({ page }).analyze()`
  - Asserts `violations.filter(v => v.impact === "critical" || v.impact === "serious").length === 0`
- **Any component/page fixes** triggered by local axe runs before committing (scope stays within `frontend/src/**`)

**H2 -- devops-agent:**

- `.github/workflows/ci.yml` -- add `a11y-check` job:
  - Runs after `e2e-tests`
  - Executes `cd frontend && npx playwright test tests/e2e/a11y.spec.ts`
  - Gated by `if: hashFiles('frontend/tests/e2e/a11y.spec.ts') != ''` so it's a no-op on the repo without the test

### 01f Pre-flight protocol

1. `python scripts/preflight_dispatch.py --agent frontend-agent --files <H1 file list>` -> exit 0
2. `python scripts/preflight_dispatch.py --agent devops-agent --files <H2 file list>` -> exit 0
3. Verify no file overlap.
4. Dispatch both in a single message. Record timing events per handoff.

### 01f Handoffs

**H1 -- frontend-agent:**
- Preamble.
- Rule 1: `frontend-design` only if a component file is modified to fix a violation.
- Rule 2: `simplify` -> receipt `01f-H1-frontend-agent.md`.
- Rule 3:
  - `cd frontend && npm install` -> exit 0
  - `cd frontend && npx playwright test tests/e2e/a11y.spec.ts` -> exit 0 (0 critical/serious violations)
  - `pre-commit run --files <changed>` -> exit 0

**H2 -- devops-agent:**
- Preamble.
- Rule 1 (dual-platform): n/a -- GitHub Actions is cloud-only.
- Rule 2: `simplify` -> receipt `01f-H2-devops-agent.md`.
- Rule 3:
  - `pipx run yamllint .github/workflows/ci.yml` -> exit 0
  - `pre-commit run --files .github/workflows/ci.yml` -> exit 0

### 01f Testing Requirements (additions)

40. `npx playwright test tests/e2e/a11y.spec.ts` -> 0 critical/serious violations.
41. `pipx run yamllint .github/workflows/ci.yml` exits 0.
42. New `a11y-check` CI job exists in ci.yml.
43. CI green on both H1 and H2 commits, including the new `a11y-check` job running green once both land.

### 01f Risks (additions)

| # | Risk | Mitigation |
|---|------|------------|
| R1.14 | Axe-core violations in 01c/01d may require re-visiting components in 01f, creating churn. | Time-box fixes to one session. If unresolvable, waive with justification in `TESTING_GATE.md`. |
| R1.15 | Axe runs flaky against async-rendering Next pages. | Always `await page.waitForLoadState("networkidle")` before analyzing. |

---

## Historical context

Phase 00 retrospective findings that shape Phase 01 execution:

- **Cross-platform discipline** (Phase 00a): every dep and script must work on Windows (Git Bash) and macOS. `next/font/google` download is cross-platform. `@axe-core/playwright` wheel ships for both OSes.
- **Rule 3 = execute configs** (Phase 00b): every config string must be exercised by its real consumer. In Phase 01 this means `npm run build`, `npx playwright test`, `npx vitest run` -- not just lint/type-check.
- **Parallel dispatch** (Phase 00g, 00h): independent handoffs MUST dispatch in a single message. Phase 01 tests same-agent parallel for the first time (01c, 01f H1+H2 where H2 is cross-agent).
- **Background CI watch** (Phase 00i): `gh run watch --exit-status` runs in background after push; main session continues. Blocking watch only at sub-phase close.
- **Handoff timing observability** (Phase 00i H4): record dispatch-start, dispatch-end, commit, ci-green/red for every handoff via `scripts/log_handoff_timing.py`. At sub-phase close, run `summary --phase 01<letter>`.
- **Simplify receipts** (Phase 00i): every source-touching handoff needs a receipt in `simplify-receipts/`. Claim `waived -- <reason>` only when there is genuinely no logic to simplify (translation seed files, one-line docstrings, etc.).
- **Governance file ownership** (Phase 00i H3): `.claude/scope.yaml`, `.claude/settings.json`, `.claude/agents/*.md` are main-session-only. No shipping agent can self-amend permissions.
