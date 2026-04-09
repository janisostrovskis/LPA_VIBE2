# Phase 01: Design System & Layout Shell

> **Revision note (2026-04-09):** This PLAN.md supersedes the initial
> scaffold committed at `7cd939f`. The original plan referenced
> `docs/LPA_DESIGN_LANGUAGE.MD` v1.0 (Songer + Montserrat + Winterlady,
> flat `--lpa-*` tokens, 1px-border cards, sticky top header). After
> Stitch MCP exploration discovered a pre-existing LPA design project
> with a materially different active system ("Sage & Canvas"), the
> doc was rewritten to v2.0 and this plan was rewritten in the same
> commit to reference it. See Section "Historical context" at the
> bottom of this file for details.

## Objective

Ship the LPA design system and layout shell in code, reconciled with
Stitch "Sage & Canvas" as the active visual spec. This means
**Material Design 3 tokens** (sourced from Stitch, ~40 colors)
implemented in Tailwind; **Epilogue + Manrope** fonts loaded via
`next/font/google` (no proprietary font files); six UI primitives
(Button gradient-primary, Card no-border, Input underline-or-filled,
Modal glassmorphism, Badge chip, Toast glassmorphism); four layout
components (Header sticky-glassmorphism, Footer, MobileNav
full-screen-drawer, LanguageSwitcher); `next-intl` wired into
`[locale]/layout.tsx`; **dual navigation pattern** (desktop sticky
top header + mobile floating bottom-dock "Sanctuary Bar"); static
placeholder pages for every public route in LV/EN/RU; and automated
WCAG 2.2 AA verification via `@axe-core/playwright` backed by a CI
gate.

No backend work. Phase 01 touches zero files under `backend/**`.

Phase 01 is the **first phase to ship real UI**. Phase 0 built the
guardrails; Phase 01 proves they hold when the repo fills with actual
application code built against a real design system.

## Prerequisites

- Phase 0 complete: all 9 sub-phases (00a-00i) landed green on master.
- Frontend scaffold (00c) exists: Next 15 + React 19 + TS strict +
  Tailwind 3.4 + ESLint flat + Vitest + Playwright configured.
- **`docs/LPA_DESIGN_LANGUAGE.MD` is at v2.0 or later** with Stitch
  "Sage & Canvas" tokens, Epilogue + Manrope fonts, no-line rule, and
  mobile-first dual navigation. **Phase 01 execution is blocked if
  doc is still at v1.0.** This revision commit advances the doc.
- `frontend/tailwind.config.ts` currently has the v1.0 `lpa-*` token
  set (11 color tokens, single card radius, no typography scale, no
  backdropBlur). Sub-phase 01a replaces it with the v2.0 Material
  token set.
- `frontend/src/app/globals.css` has the v1.0 `:root` block. 01a
  replaces it.
- `frontend/src/app/[locale]/layout.tsx` is a no-op passthrough with
  hard-coded `generateStaticParams`. 01b wires `next-intl`.
- `frontend/src/components/`, `frontend/public/locales/` do not
  exist yet. `next-intl` and `@axe-core/playwright` are not installed.
- `scripts/hooks/commit_msg_simplify_gate.py` has an unfixed Windows
  cp1257 decode bug. All planning + docs files must stay ASCII-only
  until the bug is fixed (filed in `7cd939f` commit body).

## Deliverables

Per `planning/MASTER_PLAN.md` lines 268-283, updated with v2.0 design
language:

1. `frontend/tailwind.config.ts` with the full Material Design 3 token
   set from Stitch "Sage & Canvas" and brand anchor aliases
2. Font loading via `next/font/google`: Epilogue (display + headline)
   + Manrope (body + label + UI)
3. UI primitives in `frontend/src/components/ui/`: Button, Card,
   Input, Modal, Badge, Toast -- all no-border, pill-CTA, surface-tier
   backgrounds, glassmorphism where specified
4. Layout components: Header (sticky glassmorphism), Footer,
   MobileNav (overlay drawer), LanguageSwitcher, BottomDock
   ("Sanctuary Bar" mobile-only)
5. `frontend/src/app/[locale]/layout.tsx` with i18n routing via
   `next-intl`
6. Static placeholder pages for all 12 public routes in LV/EN/RU (36
   renderable URLs)
7. WCAG 2.2 AA compliance verified on all interactive primitives and
   pages via `@axe-core/playwright`

## Sub-phases

| Sub-phase | Scope | Owners | Status |
|-----------|-------|--------|--------|
| **01a** | Material token expansion + Epilogue/Manrope font loading. Extend Tailwind with ~40 Material tokens under `lpa.*` namespace, add pill radius + cloud shadow + backdrop blur utilities, add rem-based type scale. Load fonts via `next/font/google`. Rewrite globals.css. Smoke-test on `[locale]/page.tsx` hero. | frontend-agent (H1) | Not started |
| **01b** | `next-intl` infrastructure: install package, seed LV/EN/RU `common.json` files, create `src/lib/i18n.ts` loader, add `src/middleware.ts`, wire `NextIntlClientProvider` into `[locale]/layout.tsx`. | i18n-agent (H1) -> frontend-agent (H2) -- **sequential** | Not started |
| **01c** | UI primitives: Button (gradient), Card (no-border), Badge (chip) as H1; Input (underline/filled), Modal (glassmorphism), Toast (glassmorphism) as H2. Vitest unit tests covering render, keyboard, a11y. First real test of same-agent parallel dispatch. | frontend-agent x 2 -- **parallel** | Not started |
| **01d** | Dual-nav layout shell: desktop sticky glassmorphism Header + mobile floating BottomDock, plus Footer, MobileNav drawer, LanguageSwitcher. Wire into `[locale]/layout.tsx`. | frontend-agent (H1) | Not started |
| **01e** | Placeholder pages for 12 public routes x 3 locales (36 URLs). Home/trainings/membership/directory reference Stitch screens for visual truth; other pages use plain placeholders. | i18n-agent (H1) -> frontend-agent (H2) -- **sequential** | Not started |
| **01f** | Accessibility verification: `@axe-core/playwright` e2e test visiting all 36 URLs + glassmorphism-contrast checks, plus CI `a11y-check` job gated by `hashFiles()`. | frontend-agent (H1) \|\| devops-agent (H2) -- **parallel** | Not started |

**Dependency chain:** 01a -> 01b -> 01c -> 01d -> 01e -> 01f.

**Parallel dispatch:**

- 01c H1 + H2 both frontend-agent, disjoint file sets -- first test
  of same-agent parallel.
- 01f H1 + H2 cross-agent (frontend-agent + devops-agent), disjoint
  file sets.

## Agent Assignments

| Path / deliverable | Owner | Rationale |
|--------------------|-------|-----------|
| `planning/phase-01-design-system/PLAN.md` (this file) | main-session | `planning/**` is main-session scope per `.claude/scope.yaml`. |
| `planning/phase-01-design-system/HANDOFF_LOG.md` | all agents (via `planning/**/HANDOFF_LOG.md` carve-out) | Each handoff appends an entry. |
| `docs/LPA_DESIGN_LANGUAGE.MD` | main-session | `docs/**` is main-session scope. Updated in the revision commit preceding 01a. |
| `frontend/tailwind.config.ts`, `frontend/src/app/**`, `frontend/src/components/**`, `frontend/public/fonts/**` | frontend-agent | Design system + component library + pages. |
| `frontend/src/lib/i18n.ts`, `frontend/src/lib/i18n/**`, `frontend/public/locales/**` | i18n-agent | Translation files + i18n loader per scope.yaml explicit assignment. |
| `frontend/package.json`, `frontend/package-lock.json` | frontend-agent | Shared with devops-agent; Phase 01 assigns to frontend-agent because all new deps are frontend-local (`next-intl`, `@axe-core/playwright`, possibly Radix). |
| `frontend/src/middleware.ts` | frontend-agent (via `frontend/src/**`) | Next.js locale middleware; not in i18n-agent explicit allow list. |
| `.github/workflows/ci.yml` | devops-agent | CI configuration. |
| `frontend/tests/e2e/**` | frontend-agent | E2E test files. |

## Scope ownership resolutions

| Path | Overlap | Phase 01 owner |
|------|---------|----------------|
| `frontend/src/lib/i18n.ts` | i18n-agent + frontend-agent (via `src/**`) | **i18n-agent** |
| `frontend/src/lib/i18n/**` | i18n-agent + frontend-agent | **i18n-agent** |
| `frontend/package.json`, `frontend/package-lock.json` | frontend-agent + devops-agent | **frontend-agent** |
| `frontend/tailwind.config.ts` | frontend-agent + devops-agent (via `*.config.*`) | **frontend-agent** |
| `frontend/src/app/[locale]/layout.tsx` | frontend-agent only | frontend-agent |
| `frontend/public/locales/**` | i18n-agent only | i18n-agent |
| `frontend/public/fonts/**` | frontend-agent only (via `public/**`) | frontend-agent (but no files to drop -- v2.0 uses next/font/google) |

## Acceptance Criteria

Business case `docs/LPA_BUSINESS_CASE.MD` sections:

- **3.9 Multilingual (LV/EN/RU):** language switcher present across
  site, user preference remembered, pages + emails in LV/EN/RU, URLs
  reflect language.
- **3.14 Accessibility & Inclusivity:** WCAG 2.2 AA conformance --
  color contrast, keyboard navigation, screen-reader labeling, error
  messaging, focus states, plain-language content on Join/Trainings/
  Directory pages.
- **3.17 Brand & UX Guidelines:** clean accessible visual style with
  limited palette, consistent components (buttons, forms, cards,
  badges), clear CTAs, professional/warm/trustworthy tone.

## Phase 01 testing gate

Runs at sub-phase **01f** close before the phase is declared complete.

1. **Design tokens match v2.0 spec.** Manual comparison of
   `frontend/tailwind.config.ts` + `frontend/src/app/globals.css`
   against `docs/LPA_DESIGN_LANGUAGE.MD` Section 1.2 -- every Material
   token from the Sage & Canvas snapshot is present by exact key name.
2. **Fonts render.** Epilogue and Manrope load via `next/font/google`
   (verified by `npm run build` log -- should show
   `next/font: Downloaded Epilogue/Manrope`). Latin Extended subsets
   cover Latvian diacritics.
3. **Keyboard nav works.** Tab from Header through content to Footer
   with visible focus at every stop. BottomDock is keyboard-reachable
   on mobile viewport.
4. **Language switcher changes URL.** On `/lv/about`, clicking EN
   navigates to `/en/about`. Verified in Playwright.
5. **All 12 routes x 3 locales render.** `frontend/tests/e2e/routes.spec.ts` green.
6. **WCAG AA primitives pass axe.** `frontend/tests/e2e/a11y.spec.ts`
   green (0 critical/serious violations). Includes specific checks for
   glassmorphism elements (contrast against varying background
   content).
7. **Mobile nav at 375px.** Playwright runs with
   `viewport: { width: 375, height: 812 }`. BottomDock fits and is
   usable; MobileNav drawer opens and closes via keyboard.
8. **CI fully green.** All existing 9 jobs plus new `a11y-check` = 10
   jobs pass on master.
9. **Handoff log valid.** `python scripts/check_handoff_log.py` ->
   exit 0; every source-touching entry dated 2026-04-09+ has a
   simplify receipt under `simplify-receipts/`.
10. **Sub-phases table updated.** All 6 rows flipped to **Complete**.
11. **TESTING_GATE.md written** per rulebook section B.4.
12. **SECURITY_REVIEW.md written** per rulebook section B.3. Phase 01
    is UI-only; most checks are N/A. CSP headers, XSS on rendered user
    content, and `npm audit` apply.
13. **RETROSPECTIVE.md written** with findings (same-agent parallel
    dispatch behavior, Material token mapping challenges, any
    glassmorphism contrast violations, Stitch reconciliation lessons).

Post-gate: **Phase 2 (Accounts & Authentication) unblocks.**

## Phase-level risks

| # | Risk | Mitigation |
|---|------|------------|
| R1.B | `next-intl` v3+ API may shift under Next 15. | 01b H2's Rule 3 runs `npm run build` -- build-time validation catches version drift. Downgrade to last working v3 minor if broken. |
| R1.C | Axe-core may flag violations in 01c/01d components. | Time-box fixes to one session. Unresolvable violations become retrospective findings with justified waivers. |
| R1.D | Scope ambiguity: `frontend/src/lib/i18n.ts`, `frontend/package.json`, `frontend/tailwind.config.ts` in multiple agent allow lists. | Resolutions table above explicitly assigns owners. |
| R1.E | Same-agent parallel dispatch (01c H1 + H2, both frontend-agent) is untested. First attempt may serialize. | Accept wall-clock cost on first attempt. File retrospective note on observed behavior -- no functional impact if serialized. |
| R1.F | Frontend-design skill is mandatory per Rule 1 but not hook-enforced. | Explicit "Rule 1: invoke `frontend-design` skill BEFORE editing any UI file" in every handoff brief. Main session spot-checks reply for skill invocation output. |
| R1.G | 01e creates 12 pages x 3 locales = 36 routes; TypeScript compile time may grow. | Accept for Phase 01. If `npm run build` exceeds 60s in 01e H2 verification, split into `public` + `legal` handoffs. |
| R1.K | Material token count (~40) makes Tailwind config lengthy and prone to typos vs. the Section 1.2 spec. | 01a H1 terminates with a verification step that asserts every Section 1.2 token name exists in `tailwind.config.ts` by exact key name. Doc v2.0 is authoritative. |
| R1.L | Gradient primary CTAs, glassmorphism nav, organic blobs may be non-trivial in Tailwind alone. | Use CSS custom properties in globals.css for gradient + glassmorphism utilities; Tailwind arbitrary values for one-off cases; document any Tailwind plugin adoption in simplify receipt. |
| R1.M | Desktop top header and mobile bottom dock both consume vertical space on short viewports. | Bottom dock is fixed position with backdrop-blur so content scrolls behind. All mobile pages add `lpa-xl` (48px) bottom padding. Verified in Playwright at 375x812. |
| R1.N | Stitch project `2147031711425332256` may be deleted or API key revoked; references in this plan become dangling. | `docs/LPA_DESIGN_LANGUAGE.MD` v2.0 Sections 1.2 and 11 contain the full token spec inline. Stitch references are supplementary visual aids, not hard dependencies. Phase 01 executes even if Stitch is offline. |
| R1.O | Stitch active design system may change as the user iterates. | Doc v2.0 snapshots the state as of 2026-04-09. Future Stitch evolution triggers a doc minor bump (2.0 -> 2.1) and a planning retrospective entry. Frozen snapshot protects in-flight Phase 01 from churn. |
| R1.P | Glassmorphism elements with `backdrop-filter: blur()` may fail WCAG contrast depending on scroll-position background content. | 01f adds explicit axe contrast checks at multiple scroll positions for header, bottom dock, and modal overlays. Fallback: reduce backdrop-blur opacity + add subtle solid fill if violations appear. |
| R1.Q | `commit_msg_simplify_gate.py` cp1257 bug blocks any commit whose staged diff contains UTF-8 multi-byte characters. | Planning + docs files stay ASCII-only until the hook is fixed. 01a or 01b opens a pre-handoff devops-agent patch to fix the hook (single-line change: add `encoding="utf-8", errors="replace"` to the subprocess.run call). |

## Out of scope (phase-level)

- **Real translation content.** 01b and 01e seed minimal keys only.
- **Authenticated layout.** `(auth)/**` routes are Phase 2.
- **Admin layout.** `(admin)/**` routes are Phase 8.
- **Real content on public pages.** Content population is Phase 10.
- **Backend work.** Phase 01 touches zero files under `backend/**`.
- **Payment provider selection.** Phase 3.
- **Dark mode.** Not specified in v2.0 design language.
- **Error boundary UI / 404 / 500 pages.** Defer unless 01f axe run
  requires them.
- **CMS integration.** Future phase.
- **Email template design.** Phase 9.
- **Stitch write operations.** No `apply_design_system`, `create_*`,
  `edit_screens`, `generate_*`. Read-only Stitch use.
- **Downloading Stitch HTML to the repo.** Implementers pull live via
  `mcp__stitch__get_screen` using screen IDs from the doc Section 11.

---

## Sub-phase 01a: Material tokens + Epilogue/Manrope

**Goal:** Replace v1.0 Tailwind token block with the full Material
Design 3 token set from Stitch "Sage & Canvas" per doc Section 1.2.
Load Epilogue and Manrope via `next/font/google`. Rewrite globals.css
with Material tokens, body font defaults, tonal-layering comment
block, and `prefers-reduced-motion` rule. Smoke-test on the existing
`[locale]/page.tsx` hero.

**Owner:** frontend-agent (single handoff H1). Pure design-system
expansion -- no i18n or routing.

### 01a Deliverables

1. `frontend/tailwind.config.ts` -- replace existing `extend.colors.lpa`
   block with the full Material token set (~40 tokens) plus the 4
   brand anchors (`ink`, `sage`, `beige`, `canvas`). Add or update:
   - `borderRadius`: `card: "1rem"`, `card-md: "1.5rem"`,
     `card-lg: "2rem"`, `pill: "9999px"` (remove the old `card: 12px`).
   - `boxShadow`: `cloud: "0 12px 32px rgba(28,27,27,0.06)"`,
     `cloud-lift: "0 20px 60px rgba(28,27,27,0.05)"`.
   - `backdropBlur`: `nav: "20px"`, `modal: "40px"`.
   - `fontFamily`: `display`, `headline`, `body`, `label` using
     `var(--font-epilogue)` and `var(--font-manrope)` with Epilogue
     fallbacks (Cormorant Garamond, Georgia, serif) and Manrope
     fallbacks (Inter, system-ui, sans-serif).
   - `fontSize`: full rem-based scale (display-lg, display-md,
     headline-lg, headline-md, title-lg, body-lg, body-md, label-md,
     label-sm) with lineHeight + letterSpacing tokens per doc
     Section 9.
   - `spacing`: semantic aliases `lpa-xs` through `lpa-xxxl` mapped to
     the rem equivalents of 8/16/24/32/48/64/96 px.
   - Copy verbatim from `docs/LPA_DESIGN_LANGUAGE.MD` Section 9 to
     guarantee token key parity.
2. `frontend/src/app/layout.tsx` -- import Epilogue and Manrope from
   `next/font/google` with weights 400/500/600/700 and Latin Extended
   subsets, expose as CSS vars `--font-epilogue` and `--font-manrope`,
   apply classes on `<html>`. Set `<body>` class to
   `font-body bg-lpa-surface text-lpa-on-surface` (all Tailwind v2.0
   classes).
3. `frontend/src/app/globals.css` -- rewrite:
   - `:root` block with the full `--lpa-*` Material token set from
     doc Section 1.2 (copy verbatim)
   - Body rule: `font-family: var(--font-manrope), Inter, system-ui, sans-serif; font-size: 1rem; line-height: 1.6;`
   - Background: `background: var(--lpa-surface);`
   - Text color: `color: var(--lpa-on-surface);`
   - Tonal layering comment block explaining the no-line rule
   - `@media (prefers-reduced-motion: reduce)` rule per doc Section 8
4. `frontend/src/app/[locale]/page.tsx` -- update hero to use the new
   typography classes (`text-display-lg`, `font-display`,
   `text-lpa-on-surface`, `bg-lpa-surface`, `p-lpa-xxl`) as
   end-to-end sanity check.
5. **Delete `frontend/public/fonts/README.md`** and **delete
   `frontend/public/fonts/.gitkeep`** if they exist from a prior
   attempt. v2.0 uses next/font/google exclusively -- no local
   font files to receive.
6. (optional) Trivial vitest assertion if the existing smoke test
   needs the new class names.

### 01a Handoff -- H1 (frontend-agent)

- **Preamble:** the mandatory "Execute the following. This is not a
  planning task..." sentence per CLAUDE.md "Subagent dispatch
  preamble".
- **Rule 1:** invoke `frontend-design` skill **before** editing any
  file under `frontend/src/app/**` or `frontend/tailwind.config.ts`.
- **Rule 2:** invoke `simplify` on changed files -> receipt
  `planning/phase-01-design-system/simplify-receipts/01a-H1-frontend-agent.md`.
- **Rule 3 verification** (terminal):
  - `cd frontend && npm install` -> exit 0 (if package-lock changed)
  - `cd frontend && npm run build` -> exit 0 (full Next build)
  - `cd frontend && npx vitest run` -> exit 0
  - `cd frontend && npx playwright test` -> exit 0 (smoke test still
    renders `/lv`)
  - **Token parity check**: a shell one-liner grepping
    `docs/LPA_DESIGN_LANGUAGE.MD` Section 9 for every `"..." :` pair
    and asserting the same key exists in `frontend/tailwind.config.ts`
    -- zero missing tokens allowed.
  - `python scripts/check_file_size.py` -> exit 0
  - `pre-commit run --files <changed>` -> exit 0
- **Timing:** main session records dispatch-start, dispatch-end,
  commit, ci-green/red events via
  `scripts/log_handoff_timing.py --phase 01a --handoff H1`.

### 01a Testing Requirements

1. `cd frontend && npm run build` exits 0 with the new Tailwind
   config + font imports.
2. `cd frontend && npx vitest run` exits 0.
3. `cd frontend && npx playwright test` exits 0 (existing `smoke.spec.ts`).
4. `/lv` renders with Epilogue display heading and Manrope body.
   Network tab shows successful Google Fonts downloads via
   `next/font`.
5. Token parity: every `--lpa-*` key in doc Section 1.2 and every
   Tailwind color key in doc Section 9 is present in the actual
   `tailwind.config.ts` + `globals.css` files.
6. `frontend/public/fonts/` is either absent or contains no leftover
   v1.0 README / .gitkeep files.
7. `python scripts/check_file_size.py` exits 0.
8. `python scripts/check_cola_imports.py` exits 0.
9. `python scripts/check_handoff_log.py` exits 0 (new 01a H1 entry valid).
10. `pre-commit run --all-files` passes.
11. CI green on master (all existing 9 jobs).

### 01a Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1.1 | Token typos -- 40 keys x copy-paste risk. | Token parity check in Rule 3 verification (grep-compare doc Section 9 to config). |
| R1.2 | `next/font/google` requires network access at build time. | Next.js caches downloaded fonts; first CI run downloads, subsequent runs hit cache. Same behavior as any next/font project. |
| R1.3 | Tailwind 3.4 may not support all `color-mix()` / `oklch()` CSS functions used in globals.css gradients. | Fall back to `rgba(...)` for transparent variants if build errors. Document in simplify receipt. |

---

## Sub-phase 01b: i18n infrastructure (next-intl)

**Goal:** Install `next-intl`, seed LV/EN/RU `common.json` message
files, create the i18n loader, add locale middleware, wire
`NextIntlClientProvider` into `[locale]/layout.tsx`.

**Owners:** i18n-agent (H1) -> frontend-agent (H2). **Sequential** --
H2's `middleware.ts` and `[locale]/layout.tsx` import from H1's
`src/lib/i18n.ts`.

### 01b Deliverables

**H1 -- i18n-agent (4 files):**

- `frontend/src/lib/i18n.ts` -- exports
  `locales = ["lv","en","ru"] as const`, `defaultLocale = "lv"`,
  `type Locale = typeof locales[number]`, and a `getMessages(locale)`
  async loader that reads `public/locales/<locale>/common.json` via
  dynamic import or `fs`.
- `frontend/public/locales/lv/common.json` -- seed ~20 keys: site
  name, nav labels (home/about/join/trainings/directory/news/
  resources/verify/contact), footer legal (privacy/terms/cookies),
  common UI (loading, error, closeMenu), language names. Content in
  Latvian.

  **Note:** the JSON file will contain Latvian diacritics (a-macron,
  e-macron, i-macron, l-cedilla, s-caron, u-macron -- code points
  U+0101, U+0113, U+012B, U+013C, U+0161, U+016B) which are UTF-8
  multi-byte. This will re-trigger the
  `commit_msg_simplify_gate.py` cp1257 bug at commit time. **01b H0
  pre-step** (devops-agent, one-line fix): add
  `encoding="utf-8", errors="replace"` to
  `scripts/hooks/commit_msg_simplify_gate.py` line 80ish. The same
  fix should be applied to `scripts/check_handoff_log.py` if it uses
  the same pattern. Until H0 ships, 01b H1 cannot commit.
- `frontend/public/locales/en/common.json` -- same keys, English
- `frontend/public/locales/ru/common.json` -- same keys, Russian
  (Cyrillic, also UTF-8 multi-byte; H0 must ship first)

**H0 -- devops-agent (1 file, pre-requisite):**

- `scripts/hooks/commit_msg_simplify_gate.py` -- fix line ~80 to pass
  `encoding="utf-8", errors="replace"` to the
  `subprocess.run(["git","diff","--cached","--", path], ...)` call.
- Also inspect `scripts/check_handoff_log.py` and apply the same fix
  if it calls subprocess with `text=True` but no explicit encoding.
- Rule 3: add a selftest that runs `git diff` against a fixture file
  containing a multi-byte UTF-8 character (e.g. Latvian "Kl[U+013C][U+016B]da") and
  asserts the hook does not crash.
- Commit in its own commit before 01b H1 dispatches.

**H2 -- frontend-agent (5 files):**

- `frontend/package.json` -- add `"next-intl": "<pinned>"`. Pin to the
  current compatible version via `npm view next-intl version` -- no
  invented versions.
- `frontend/package-lock.json` -- regenerated by `npm install`.
- `frontend/src/middleware.ts` -- `createMiddleware` from
  `next-intl/middleware`, matcher
  `"/((?!api|_next|.*\\..*).*)"`, `locales` and `defaultLocale`
  imported from `@/lib/i18n`.
- `frontend/src/app/[locale]/layout.tsx` -- wrap children in
  `<NextIntlClientProvider messages={await getMessages(locale)}>`.
  Replace the hand-rolled `generateStaticParams` with next-intl's
  pattern.
- `frontend/src/app/layout.tsx` -- ensure bare passthrough. Keep
  `<html>` class list from 01a (next/font vars).
- `frontend/src/app/page.tsx` -- keep `redirect("/lv")` or let
  next-intl middleware handle root redirect.
- `frontend/tests/e2e/i18n.spec.ts` -- new e2e test visiting `/lv`,
  `/en`, `/ru` and asserting each renders its localized site name.

### 01b Handoffs

**H0 -- devops-agent** (first, blocks H1):
- Preamble.
- Rule 2: `simplify` -> receipt `01b-H0-devops-agent.md`.
- Rule 3:
  - `python scripts/hooks/commit_msg_simplify_gate.py --selftest` -> exit 0 (new selftest)
  - `pre-commit run --files scripts/hooks/commit_msg_simplify_gate.py` -> exit 0

**H1 -- i18n-agent** (after H0 commits):
- Preamble.
- Rule 2: `simplify` -> receipt `01b-H1-i18n-agent.md` (likely
  `waived -- seed JSON + thin loader wrapper, no logic to simplify`).
- Rule 3:
  - `cd frontend && npx tsc --noEmit` -> exit 0 (i18n.ts compiles)
  - `python -c "import json; [json.load(open(f'frontend/public/locales/{l}/common.json')) for l in ('lv','en','ru')]"` -> exit 0
  - Key parity check across all three locale files
  - `pre-commit run --files <changed>` -> exit 0

**H2 -- frontend-agent** (after H1 commits):
- Preamble.
- Rule 1: `frontend-design` skill before touching `[locale]/layout.tsx`.
- Rule 2: `simplify` -> receipt `01b-H2-frontend-agent.md`.
- Rule 3:
  - `cd frontend && npm install` -> exit 0
  - `cd frontend && npm run build` -> exit 0
  - `cd frontend && npx vitest run` -> exit 0
  - `cd frontend && npx playwright test tests/e2e/smoke.spec.ts tests/e2e/i18n.spec.ts` -> exit 0
  - `pre-commit run --files <changed>` -> exit 0

### 01b Testing Requirements

12. `scripts/hooks/commit_msg_simplify_gate.py` no longer crashes on
    multi-byte UTF-8 staged diffs (H0).
13. `frontend/src/lib/i18n.ts` type-checks clean.
14. All three `common.json` files parse and have identical key trees.
15. `cd frontend && npm install` resolves `next-intl`.
16. `cd frontend && npm run build` passes with `next-intl` wired.
17. `/` redirects to `/lv`. `/lv`, `/en`, `/ru` all render with
    localized site names.
18. `i18n.spec.ts` e2e test green.
19. CI green on all three H0/H1/H2 commits.

### 01b Risks

| # | Risk | Mitigation |
|---|------|------------|
| R1.4 | `next-intl` v3 requires config at `src/i18n/request.ts` not `src/lib/i18n.ts`. | If required, frontend-agent creates `src/i18n/request.ts` (in `src/**` scope) and imports helpers from i18n-agent's `src/lib/i18n.ts`. Document in receipt. |
| R1.5 | H0 devops fix may expose further encoding bugs in other hooks. | Rule 3 selftest in H0 covers the immediate case; any further crashes are filed as fresh findings and fixed in follow-up commits. |

---

## Sub-phase 01c: UI primitives

**Goal:** Build 6 UI primitives per v2.0 spec. Each component uses
only v2.0 Tailwind classes (no ad-hoc hex codes), has visible
focus-visible state, passes vitest unit tests, and is TS-strict clean.

**Owner:** frontend-agent x 2 -- **parallel dispatch** in a single
message.

### 01c Deliverables

**H1 -- Button / Card / Badge:**

- `frontend/src/components/ui/Button.tsx`:
  - Variants: `primary` (gradient 135deg `lpa-primary` ->
    `lpa-primary-container`, pill radius, uppercase `label-md`,
    letter-spacing 0.1em, min-height 56px), `secondary`
    (`lpa-secondary-container` fill, `lpa-on-secondary-container`
    text, pill, no border), `text` (no fill, `lpa-primary` text,
    underline on hover)
  - Props: `variant`, `size` (`sm`|`md`|`lg`), `disabled`, `loading`,
    `type`, `onClick`, `children`
  - Focus-visible: 2px `lpa-secondary` ring offset 3px
  - Active: `scale(0.98)` via Tailwind `active:scale-[0.98]`
  - Hover: optional `cloud` shadow via `hover:shadow-cloud`
- `frontend/src/components/ui/Card.tsx`:
  - Base: `bg-lpa-surface-container-lowest`, `rounded-card` (16px),
    `p-lpa-m` (24px), **no border**
  - Optional `feature` variant: `bg-lpa-surface-container`,
    `rounded-card-md` (24px), `p-lpa-l` (32px)
  - Optional `hover` prop: `hover:-translate-y-0.5 hover:shadow-cloud transition-all duration-300 ease-out`
- `frontend/src/components/ui/Badge.tsx`:
  - Variants: `primary`, `secondary` (default), `tertiary`, `outline`
  - Chip style: `rounded-pill`, `px-3 py-1.5`, `label-md` uppercase,
    `letter-spacing 0.05em`
- `frontend/src/components/ui/__tests__/Button.test.tsx`
- `frontend/src/components/ui/__tests__/Card.test.tsx`
- `frontend/src/components/ui/__tests__/Badge.test.tsx`

**H2 -- Input / Modal / Toast:**

- `frontend/src/components/ui/Input.tsx`:
  - Two style props: `variant: "underline" | "filled"`
  - Underline: bottom 1px `lpa-outline-variant` at 40% opacity,
    focus -> 2px `lpa-secondary`
  - Filled: `bg-lpa-surface-container-high`, rounded 0.5rem, floating
    label
  - Label associated via `for`/`id`; optional `hint`, `error` props
  - Error: red `#B64949` text, linked via `aria-describedby`
  - No 4-sided borders
- `frontend/src/components/ui/Modal.tsx`:
  - Overlay: `fixed inset-0 bg-lpa-surface/80 backdrop-blur-modal`
  - Content card: `bg-lpa-surface-container-lowest rounded-card-md p-lpa-l`
  - `shadow-cloud-lift` on content card
  - `<dialog>` element + focus trap (first focusable on open,
    restore on close)
  - ESC key closes; click-outside closes
  - `role="dialog" aria-modal="true" aria-labelledby={titleId}`
  - Portal to `document.body`
  - **Decision point:** hand-rolled vs `@radix-ui/react-dialog`.
    Default hand-rolled; fall back to Radix if focus trap fragile.
    Document in receipt.
- `frontend/src/components/ui/Toast.tsx`:
  - Position: `fixed top-4 right-4` with safe z-index
  - Glassmorphism: `bg-lpa-surface-container-highest/80 backdrop-blur-nav`
  - Rounded pill + `shadow-cloud`
  - `role="status"` for info/success, `role="alert"` for error
  - Auto-dismiss after configurable timeout (default 5000ms)
  - Variants via tertiary color mapping: `success` ->
    `lpa-secondary`, `error` -> `#B64949`, `info` -> `lpa-tertiary`
- `frontend/src/components/ui/__tests__/Input.test.tsx`
- `frontend/src/components/ui/__tests__/Modal.test.tsx`
- `frontend/src/components/ui/__tests__/Toast.test.tsx`

### 01c Pre-flight protocol

Before dispatching both Agent calls in a single message:

1. `python scripts/preflight_dispatch.py --agent frontend-agent --files <H1 files>` -> exit 0
2. `python scripts/preflight_dispatch.py --agent frontend-agent --files <H2 files>` -> exit 0
3. Verify union of H1 + H2 has no duplicates.
4. Record `log_handoff_timing.py --phase 01c --handoff H1 --event dispatch-start` and same for H2.
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

### 01c Stitch screen references (for visual truth)

Implementers may pull live HTML via `mcp__stitch__get_screen` for
visual context while building components:

- **Button + Hero CTA:** "LPA Homepage (Refined)" (mobile) or "LPA
  Homepage (Desktop)"
- **Card grids:** "Trainings Catalogue (Refined)" or "Membership
  Plans (Refined)"
- **Chip/Badge:** "Directory (Refined)" filter chips
- **Input:** "Member Dashboard (Refined)" profile form
- **Modal:** (no direct reference; use doc Section 5.4 spec)
- **Toast:** (no direct reference; use doc Section 5.5 pattern)

Stitch project: `2147031711425332256`. Screens list:
`mcp__stitch__list_screens --projectId 2147031711425332256`.

### 01c Testing Requirements

20. All 6 component test files pass.
21. `cd frontend && npm run build` exits 0 with new components.
22. Each component exports a named type for its props.
23. TypeScript strict mode clean -- no `any`, no `@ts-ignore`.
24. No ad-hoc hex codes outside `#B64949` (error color, per doc
    Section 5.2.3).
25. Focus states verified in Playwright snapshot tests or manual check.
26. CI green on both H1 and H2 commits.

---

## Sub-phase 01d: Dual-nav layout shell

**Goal:** Build the dual-navigation layout shell -- desktop sticky
glassmorphism Header with horizontal nav + mobile floating BottomDock
"Sanctuary Bar" -- plus Footer, MobileNav drawer, and LanguageSwitcher.
Wire everything into `[locale]/layout.tsx`.

**Owner:** frontend-agent (single handoff H1). Header, BottomDock,
and MobileNav share state (menu open/close) so a single handoff keeps
coordination costs low.

### 01d Deliverables

- `frontend/src/components/layout/Header.tsx`:
  - `sticky top-0 h-20 bg-lpa-surface/80 backdrop-blur-nav z-100`
  - Scroll-shadow: add `shadow-cloud` via client-side scroll listener
  - Logo left (placeholder SVG or text-only "LPA"), horizontal nav
    center (desktop only), LanguageSwitcher + CTA right
  - Nav items: `font-label uppercase text-label-md font-medium tracking-[0.08em] text-lpa-on-surface hover:text-lpa-secondary`
  - Active: `text-lpa-secondary border-b-2 border-lpa-secondary`
  - Hide horizontal nav below `md` breakpoint; show hamburger instead
- `frontend/src/components/layout/BottomDock.tsx`:
  - `fixed bottom-6 left-1/2 -translate-x-1/2 md:hidden`
  - `bg-lpa-surface/80 backdrop-blur-nav rounded-pill shadow-cloud px-4 py-3 flex gap-2`
  - Icon nav items (Home, Trainings, Directory, News, Profile):
    24px icon + `label-sm` caption, `min-h-12 min-w-12` tap targets
  - Active item: `text-lpa-secondary`, inactive: `text-lpa-on-surface-variant`
  - Keyboard-reachable; each item has `aria-current="page"` when active
- `frontend/src/components/layout/Footer.tsx`:
  - `bg-lpa-surface-container-low py-lpa-xl px-lpa-l`
  - Columns: LPA brand info, legal links (Privacy / Terms / Cookies),
    contact, alternate LanguageSwitcher
  - Copyright line at bottom
- `frontend/src/components/layout/MobileNav.tsx`:
  - Full-screen overlay drawer (not the BottomDock; the drawer is
    the hamburger-triggered full menu)
  - Uses `Modal` primitive from 01c or a custom glassmorphism pattern
  - Stacked links 32px apart, min 48px tap targets
  - Focus trap, ESC closes, link click dismisses
  - BottomDock remains visible behind the drawer overlay
- `frontend/src/components/layout/LanguageSwitcher.tsx`:
  - Three buttons (LV/EN/RU) via `Button` primitive `text` variant
  - Active locale visually marked
  - Uses `useRouter` + `usePathname` from `next/navigation` and
    next-intl's routing helper to switch locale without full
    navigation
- `frontend/src/components/layout/__tests__/Header.test.tsx`
- `frontend/src/components/layout/__tests__/BottomDock.test.tsx`
- `frontend/src/components/layout/__tests__/MobileNav.test.tsx`
- `frontend/src/components/layout/__tests__/LanguageSwitcher.test.tsx`
- `frontend/src/app/[locale]/layout.tsx` -- modify to render
  `<Header /><main className="pb-lpa-xl md:pb-0">{children}</main><Footer /><BottomDock />`

### 01d Handoff -- H1 (frontend-agent)

- Preamble.
- Rule 1: `frontend-design` before any layout component or layout.tsx.
- Rule 2: `simplify` -> receipt `01d-H1-frontend-agent.md`.
- Rule 3 verification:
  - `cd frontend && npx vitest run src/components/layout/` -> exit 0
  - `cd frontend && npm run build` -> exit 0
  - `cd frontend && npx playwright test tests/e2e/smoke.spec.ts tests/e2e/i18n.spec.ts` -> exit 0
  - Playwright mobile viewport test: BottomDock visible + hamburger
    opens MobileNav drawer
  - `pre-commit run --files <changed>` -> exit 0

### 01d Stitch screen references

- **Desktop glassmorphism Header:** "LPA Homepage (Desktop)" -- hero
  + sticky header interaction
- **Mobile BottomDock:** "LPA Homepage (Refined)" -- floating pill at
  bottom with icon nav
- **MobileNav drawer:** (no direct reference; use doc Section 5.3.3)
- **Footer:** any desktop screen scrolled to bottom

### 01d Testing Requirements

27. Header renders nav links across `/lv`, `/en`, `/ru` with correct
    localized labels.
28. BottomDock renders on mobile viewport (375px width) and hides on
    desktop (>= 768px).
29. MobileNav drawer opens/closes via keyboard + touch; bottom dock
    remains visible behind the overlay.
30. LanguageSwitcher changes URL prefix on click (Playwright).
31. Footer renders legal links (404 expected until 01e).
32. Mobile pages have 48px bottom padding -- BottomDock does not
    cover content.
33. `npm run build` exits 0.
34. All layout component tests pass.
35. CI green.

---

## Sub-phase 01e: Placeholder pages for 12 public routes

**Goal:** Create static placeholder pages for all public routes so
the layout shell has real destinations. Home / trainings / membership
/ directory reference Stitch screens for visual truth; other pages
use plain placeholders.

**Owners:** i18n-agent (H1) -> frontend-agent (H2). **Sequential**.

### 01e Deliverables

**H1 -- i18n-agent (3 files):**

Extend `frontend/public/locales/{lv,en,ru}/common.json` with ~36
new page content keys (12 pages x ~3 keys each): `page.home.title`,
`page.home.subtitle`, `page.home.cta`, `page.about.*`, `page.join.*`,
`page.trainings.*`, `page.directory.*`, `page.news.*`,
`page.resources.*`, `page.verify.*`, `page.contact.*`,
`page.legal.privacy.*`, `page.legal.terms.*`, `page.legal.cookies.*`.

Content is placeholder text marked with `TODO: replace with real content`
where appropriate (especially legal pages).

**H2 -- frontend-agent (14 files):**

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
- `frontend/src/app/[locale]/page.tsx` -- upgrade hero to proper home
  page (Display-LG title, body-lg subtitle, primary CTA Button
  linking to `/[locale]/join`)
- `frontend/tests/e2e/routes.spec.ts` -- Playwright test parametrized
  over 12 routes x 3 locales (36 cases), asserts HTTP 200 and the
  expected `<h1>` text from the translation file

Each page: heading from `useTranslations()`, intro paragraph using
`Body-LG` class, possibly a Card from 01c. Legal pages use
`<h2>Coming soon</h2>` block + TODO comment.

### 01e Handoffs

**H1 -- i18n-agent:**
- Preamble.
- Rule 2: `simplify` -> receipt `01e-H1-i18n-agent.md` (likely
  `waived -- translation content only`).
- Rule 3: JSON syntax + key parity across three locales;
  `pre-commit run --files <changed>` -> exit 0.

**H2 -- frontend-agent** (after H1 commits):
- Preamble.
- Rule 1: `frontend-design` before any page file.
- Rule 2: `simplify` -> receipt `01e-H2-frontend-agent.md`.
- Rule 3:
  - `cd frontend && npm run build` -> exit 0
  - `cd frontend && npx playwright test tests/e2e/routes.spec.ts` -> exit 0 (36 routes return 200)
  - `cd frontend && npx vitest run` -> exit 0
  - `pre-commit run --files <changed>` -> exit 0

### 01e Stitch screen references

Implementers may pull live HTML via `mcp__stitch__get_screen` for
visual context:

- **Home page:** "LPA Homepage (Desktop)" + "LPA Homepage (Refined)"
- **Trainings:** "Trainings Catalogue (Desktop)" + "Trainings
  Catalogue (Refined)"
- **Membership:** "Membership Plans (Desktop)" + "Membership Plans
  (Refined)"
- **Directory:** "Directory (Desktop Refined)" + "Directory (Refined)"
- **Member dashboard:** "Member Dashboard (Desktop Refined)" +
  "Member Dashboard (Refined)" -- **reference only; Phase 2 work**,
  not Phase 01.
- **About / news / resources / verify / contact / legal:** no Stitch
  references. Use plain placeholder content per doc v2.0 spec.

### 01e Testing Requirements

36. All three `common.json` files have identical page-key trees.
37. `cd frontend && npm run build` passes with 12 new pages.
38. `routes.spec.ts` asserts 36 routes return 200 and `<h1>` matches
    translated title.
39. Footer legal links from 01d now resolve.
40. Home page shows Display-LG hero with CTA linking to
    `/[locale]/join`.
41. `npx vitest run` passes.
42. CI green on both commits.

---

## Sub-phase 01f: Accessibility verification

**Goal:** Confirm WCAG 2.2 AA compliance via automated axe-core
checks. Fix any critical/serious violations. Install CI gate blocking
regressions. Extra care on glassmorphism contrast given the
backdrop-blur nav / bottom-dock / modal patterns.

**Owners:** frontend-agent (H1) || devops-agent (H2). **Parallel
dispatch**.

### 01f Deliverables

**H1 -- frontend-agent:**

- `frontend/package.json` -- add `"@axe-core/playwright": "<pinned>"`
  via `npm view @axe-core/playwright version`
- `frontend/package-lock.json` -- regenerated
- `frontend/tests/e2e/a11y.spec.ts` -- Playwright test that:
  - Loads each of 12 routes x 3 locales (36 URLs)
  - For each URL, runs axe at multiple scroll positions (top, middle,
    bottom) to verify glassmorphism Header + BottomDock contrast
    against varying background content
  - `await page.waitForLoadState("networkidle")` before running axe
  - Asserts `violations.filter(v => v.impact === "critical" || v.impact === "serious").length === 0`
- **Any component/page fixes** triggered by local audit before
  committing (scope stays within `frontend/src/**`)

**H2 -- devops-agent:**

- `.github/workflows/ci.yml` -- add `a11y-check` job:
  - Runs after `e2e-tests`
  - Executes `cd frontend && npx playwright test tests/e2e/a11y.spec.ts`
  - Gated by `if: hashFiles('frontend/tests/e2e/a11y.spec.ts') != ''`

### 01f Pre-flight protocol

1. `python scripts/preflight_dispatch.py --agent frontend-agent --files <H1 files>` -> exit 0
2. `python scripts/preflight_dispatch.py --agent devops-agent --files <H2 files>` -> exit 0
3. Dispatch both in one message. Record timing per handoff.

### 01f Handoffs

**H1 -- frontend-agent:**
- Preamble.
- Rule 1: `frontend-design` if a component is modified for a fix.
- Rule 2: `simplify` -> receipt `01f-H1-frontend-agent.md`.
- Rule 3:
  - `cd frontend && npm install` -> exit 0
  - `cd frontend && npx playwright test tests/e2e/a11y.spec.ts` -> exit 0
  - `pre-commit run --files <changed>` -> exit 0

**H2 -- devops-agent:**
- Preamble.
- Rule 1 (dual-platform): n/a (GitHub Actions is cloud-only).
- Rule 2: `simplify` -> receipt `01f-H2-devops-agent.md`.
- Rule 3:
  - `pipx run yamllint .github/workflows/ci.yml` -> exit 0
  - `pre-commit run --files .github/workflows/ci.yml` -> exit 0

### 01f Testing Requirements

43. `npx playwright test tests/e2e/a11y.spec.ts` -> 0
    critical/serious violations across all 36 routes x 3 scroll
    positions = 108 audit points.
44. Glassmorphism elements pass contrast at all scroll positions.
45. `pipx run yamllint .github/workflows/ci.yml` exits 0.
46. New `a11y-check` CI job exists.
47. CI green on both H1 and H2 commits including new job.

---

## Historical context

Phase 00 retrospective findings + Phase 01 pre-execution revisions:

- **Cross-platform discipline** (Phase 00a): every dep and script
  must work on Windows (Git Bash) and macOS. Epilogue + Manrope via
  `next/font/google` are cross-platform. `@axe-core/playwright` wheel
  ships for both OSes.
- **Rule 3 = execute configs** (Phase 00b): every config string must
  be exercised by its real consumer. In Phase 01 this means
  `npm run build`, `npx playwright test`, `npx vitest run`.
- **Parallel dispatch** (Phase 00g, 00h): independent handoffs
  dispatch in a single message. Phase 01 tests same-agent parallel
  for the first time in 01c.
- **Background CI watch** (Phase 00i): `gh run watch --exit-status`
  runs in background; blocking watch only at sub-phase close.
- **Handoff timing observability** (Phase 00i H4): dispatch-start /
  dispatch-end / commit / ci-green|red recorded per handoff.
- **Simplify receipts** (Phase 00i): every source-touching handoff
  needs a receipt. Claim `waived -- <reason>` only when there is no
  logic to simplify.
- **Governance file ownership** (Phase 00i H3): `.claude/scope.yaml`,
  `.claude/settings.json`, `.claude/agents/*.md` are main-session
  only.
- **commit_msg_simplify_gate.py cp1257 bug** (Phase 01 scaffold
  commit `7cd939f`): the hook crashes on multi-byte UTF-8 in staged
  diffs on Windows. Workaround: ASCII-only planning/docs files.
  Permanent fix: 01b H0 adds `encoding="utf-8", errors="replace"` to
  the `subprocess.run` call.
- **Stitch reconciliation** (Phase 01 revision, 2026-04-09):
  `docs/LPA_DESIGN_LANGUAGE.MD` v1.0 was written before Stitch
  iteration; v2.0 reconciles to Stitch "Sage & Canvas" from project
  `2147031711425332256`. Future Stitch iterations trigger doc minor
  bumps (2.0 -> 2.1) and planning retrospective entries. Phase 01
  plan was rewritten in the same commit as the doc to stay in sync.
  Supersedes scaffold plan at `7cd939f`.
