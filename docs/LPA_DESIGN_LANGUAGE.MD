# Latvijas Pilates Asociacija Web Design Stylebook

Version: 2.0
Owner: LPA / Janis
Last updated: 2026-04-09

This document defines the visual design system for the **Latvijas Pilates
Asociacija (LPA)** website and related web properties. It is intended
for **engineers and designers** implementing UI in code (CSS / Tailwind /
design tokens).

**v2.0 reconciles the doc with the active Stitch "Sage & Canvas" design
system** maintained in Google Stitch project `2147031711425332256`
("Mobile-First App Redesign"). See Section 11 (Source of Truth) and
Section 12 (Revision History) for the upgrade path from v1.0. The full
Stitch token snapshot is embedded in Section 1 so this document remains
self-sufficient even without Stitch access.

Note on character set: this doc is intentionally **ASCII-only**. A
`scripts/hooks/commit_msg_simplify_gate.py` bug on Windows cp1257
decoding blocks commits containing multi-byte UTF-8. Any design names,
Latvian strings, or special glyphs are written in ASCII transliteration
until that hook is fixed.

---

## 0. Brand Assets

- Primary logo file (line-art Pilates pose + wordmark):
  `frontend/public/images/20210618_lpa_logo_vards_zime_white_LV.png`
- Recommended variants to ship:
  - `lpa-logo-primary.svg` -- dark lines on light background
  - `lpa-logo-inverse.svg` -- white lines for dark backgrounds
  - `lpa-logo-mark-only.svg` -- illustration only (no wordmark) for
    favicon and small spaces

### Logo Rules

- **Clear space:** at least the height of the word "LPA" on all sides.
- **Minimum digital height:** 32px.
- Never distort, stretch, rotate, change stroke width, add shadows or
  glows, or recolor to non-brand colors. Keep monochrome + accent
  versions only if explicitly defined later.

---

## 1. Design Tokens

LPA v2.0 uses a **Material Design 3 token scheme** sourced from Stitch
"Sage & Canvas". The brand identity is expressed through four anchor
colors that override Material defaults; the rest of the ~40 tokens are
derived by the Material Color Utilities algorithm and captured here
verbatim for deterministic implementation.

Two namespaces exist:

1. **Brand anchors** -- four semantic colors that describe LPA identity.
   Prefer these in component props, copy, and brand-level usage.
2. **Material tokens** -- the full computed set that Tailwind consumes
   and components reference for surfaces, states, and hierarchy.

### 1.1 Brand Anchor Colors

| Token         | Hex     | Role                                                    |
| ------------- | ------- | ------------------------------------------------------- |
| `--lpa-ink`   | #1A1A1A | Brand ink; maps to Material `primary` + `on_surface`    |
| `--lpa-sage`  | #9CAF88 | Brand accent; maps to Material `secondary`              |
| `--lpa-beige` | #E8DCC4 | Warm secondary accent; maps to Material `tertiary`      |
| `--lpa-canvas`| #FCF9F8 | Warm white canvas; maps to Material `surface` + `background` |

These are the four values that define the LPA look. All other tokens
are generated from them via Material Color Utilities tonal palettes.

### 1.2 Material Token Set (Sage & Canvas snapshot)

```css
:root {
  /* Surface hierarchy (backgrounds + fills, no borders for sectioning) */
  --lpa-surface:                    #FCF9F8;
  --lpa-surface-bright:             #FCF9F8;
  --lpa-surface-dim:                #DCD9D9;
  --lpa-surface-container-lowest:   #FFFFFF;
  --lpa-surface-container-low:      #F6F3F2;
  --lpa-surface-container:          #F0EDED;
  --lpa-surface-container-high:     #EAE7E7;
  --lpa-surface-container-highest:  #E5E2E1;
  --lpa-surface-variant:            #E5E2E1;

  /* Primary (Ink) */
  --lpa-primary:                    #5F5E5E;
  --lpa-primary-container:          #AAA8A8;
  --lpa-primary-fixed:              #E5E2E1;
  --lpa-primary-fixed-dim:          #C8C6C5;
  --lpa-on-primary:                 #FFFFFF;
  --lpa-on-primary-container:       #3E3D3D;
  --lpa-on-primary-fixed:           #1C1B1B;
  --lpa-on-primary-fixed-variant:   #474746;

  /* Secondary (Sage) */
  --lpa-secondary:                  #526442;
  --lpa-secondary-container:        #D2E6BC;
  --lpa-secondary-fixed:            #D5E9BF;
  --lpa-secondary-fixed-dim:        #B9CDA4;
  --lpa-on-secondary:               #FFFFFF;
  --lpa-on-secondary-container:     #576846;
  --lpa-on-secondary-fixed:         #111F05;
  --lpa-on-secondary-fixed-variant: #3B4C2C;

  /* Tertiary (Beige) */
  --lpa-tertiary:                   #665E4B;
  --lpa-tertiary-container:         #B2A892;
  --lpa-tertiary-fixed:             #EDE1C9;
  --lpa-tertiary-fixed-dim:         #D1C5AE;
  --lpa-on-tertiary:                #FFFFFF;
  --lpa-on-tertiary-container:      #443D2C;
  --lpa-on-tertiary-fixed:          #211B0C;
  --lpa-on-tertiary-fixed-variant:  #4D4634;

  /* Error */
  --lpa-error:                      #BA1A1A;
  --lpa-error-container:            #FFDAD6;
  --lpa-on-error:                   #FFFFFF;
  --lpa-on-error-container:         #93000A;

  /* Text + outlines */
  --lpa-on-background:              #1C1B1B;
  --lpa-on-surface:                 #1C1B1B;
  --lpa-on-surface-variant:         #44483F;
  --lpa-outline:                    #75786E;
  --lpa-outline-variant:            #C5C8BC;
  --lpa-surface-tint:               #5F5E5E;

  /* Inverse (dark overlays, toasts, snackbars) */
  --lpa-inverse-surface:            #313030;
  --lpa-inverse-on-surface:         #F3F0EF;
  --lpa-inverse-primary:            #C8C6C5;

  /* Brand anchor aliases (readable names for component props) */
  --lpa-ink:                        #1A1A1A;
  --lpa-sage:                       #9CAF88;
  --lpa-beige:                      #E8DCC4;
  --lpa-canvas:                     #FCF9F8;
}
```

### 1.3 Surface Hierarchy and the No-Line Rule

Depth is expressed by **stacking surface tiers**, not by drawing 1px
borders. A card on a page body uses `surface-container-lowest` over a
`surface-container-low` background; a nested sub-section uses
`surface-container` over `surface-container-low`. The visual hierarchy
follows the tiering order:

```
surface-container-lowest (#FFFFFF)   <- top-layer cards, inputs, elevated
surface-container-low    (#F6F3F2)   <- default section background
surface                  (#FCF9F8)   <- page body canvas
surface-container        (#F0EDED)   <- nested content blocks
surface-container-high   (#EAE7E7)   <- active/selected states, input fills
surface-container-highest(#E5E2E1)   <- deepest containers, modal backdrops
```

**Prohibited:** `border: 1px solid ...` to section content. A divider
between two list items is `surface-container-low` background padding or
48-px vertical whitespace; never an `<hr>`.

**Allowed exception ("Ghost Border" fallback):** if accessibility or
form affordance requires a visible line (for example, a focused input),
use `outline-variant` (#C5C8BC) at 15-20% opacity -- never the solid
`outline` token.

### 1.4 Gradient Textures and Glassmorphism

Primary buttons, hero surfaces, and floating elements use gradients and
backdrop-blur to break the flatness:

- **Primary CTA gradient:** `linear-gradient(135deg, var(--lpa-primary) 0%, var(--lpa-primary-container) 100%)`
- **Hero surface gradient:** same, applied as a masked background behind display headlines
- **Glassmorphism (nav, modals):** `background: color-mix(in oklch, var(--lpa-surface) 80%, transparent); backdrop-filter: blur(20px);` (nav) or `blur(40px);` (modal)

Guidelines:

- UI remains **mostly neutral**: 70-80 percent surface tones, 20-30
  percent accents.
- Avoid more than **two accent colors** per component.
- For text on images or gradients, verify WCAG 2.2 AA contrast at 4.5:1
  for normal text and 3.0:1 for large text.

---

## 2. Typography

### 2.1 Font Stacks

```css
:root {
  --lpa-font-display:  "Epilogue", "Cormorant Garamond", Georgia, serif;
  --lpa-font-headline: "Epilogue", "Cormorant Garamond", Georgia, serif;
  --lpa-font-body:     "Manrope", "Inter", system-ui, -apple-system, "Segoe UI", sans-serif;
  --lpa-font-label:    "Manrope", "Inter", system-ui, sans-serif;
}
```

- **Display + Headline (Epilogue).** A high-contrast geometric display
  serif/sans hybrid from Google Fonts. Used for hero moments, section
  openers, and "breathing" headlines. Weights 400 / 500 / 600 / 700.
  Loaded via `next/font/google` -- no proprietary files.
- **Body + Label + UI (Manrope).** A humanist geometric sans from
  Google Fonts. Used for navigation, body text, forms, buttons, labels,
  meta, and all functional text. Weights 400 / 500 / 600 / 700. Loaded
  via `next/font/google`.
- **No script accent font** in v2.0. The v1.0 "Winterlady" accent is
  dropped; editorial asymmetry now comes from whitespace and type scale,
  not from a decorative script.

### 2.2 Type Scale (mobile-first, rem-based)

| Role             | Font     | Size (rem) | Size (px) | Line-height | Tracking  |
| ---------------- | -------- | ---------- | --------- | ----------- | --------- |
| Display-LG       | Epilogue | 3.5rem     | 56px      | 1.1         | -0.02em   |
| Display-MD       | Epilogue | 2.75rem    | 44px      | 1.1         | -0.02em   |
| Headline-LG      | Epilogue | 2.25rem    | 36px      | 1.15        | -0.01em   |
| Headline-MD      | Epilogue | 1.75rem    | 28px      | 1.2         | -0.01em   |
| Title-LG         | Epilogue | 1.375rem   | 22px      | 1.3         | 0         |
| Body-LG          | Manrope  | 1rem       | 16px      | 1.6         | 0         |
| Body-MD          | Manrope  | 0.875rem   | 14px      | 1.5         | 0         |
| Label-MD         | Manrope  | 0.75rem    | 12px      | 1.4         | +0.05em UC|
| Label-SM         | Manrope  | 0.6875rem  | 11px      | 1.35        | +0.08em UC|

- **Mobile (below 768px):** display and headline sizes scale down by
  10-15 percent. Body text stays at **16px minimum**.
- **Desktop (1024px+):** Display-LG may scale up to 4.5rem (72px) for
  hero headlines.
- **Max line length:** 60-75 characters for paragraphs.
- **Labels** (buttons, nav items, chips) are uppercase with +0.05em to
  +0.08em tracking for an editorial feel.

### 2.3 Editorial Voice Rules

- Large display headlines may be center-aligned or offset to the left
  to create asymmetric tension. Body text remains grid-anchored for
  readability.
- Do not mix more than two typefaces in a single view. Epilogue and
  Manrope are the only two permitted.
- Italic is allowed in Epilogue for pull-quotes and emphasis within
  body text.
- Do not use all-caps body text. All-caps is reserved for labels
  shorter than 20 characters.

---

## 3. Layout and Spacing

### 3.1 Breakpoints

```text
mobile:    0    -  767px    (primary design target)
tablet:    768  - 1023px
desktop:   1024 - 1439px
wide:      1440px+
```

v2.0 is explicitly **mobile-first** per the Stitch project
orientation. Design every component and page starting from 390px width
and progressively enhance.

### 3.2 Grid

- Max content width: **1200-1280px**.
- Desktop: **12-column grid**, gutters 24-32px.
- Tablet: 8-column grid.
- Mobile: 4 columns or simple full-width.

### 3.3 Spacing Scale

Spacing uses the `spacingScale: 3` (relaxed) density from Stitch. All
values are multiples of 8 px:

| Token  | Value | Usage                                                |
| ------ | ----- | ---------------------------------------------------- |
| `xs`   | 8px   | Tiny gaps, icon spacing                              |
| `s`    | 16px  | Label-to-input, inline text blocks                   |
| `m`    | 24px  | Card inner padding                                   |
| `l`    | 32px  | Card margins, section inner padding                  |
| `xl`   | 48px  | Vertical space between sections (mobile)             |
| `xxl`  | 64px  | Vertical padding (desktop sections)                  |
| `xxxl` | 96px  | Hero padding, major separators                       |

- Section padding (desktop): 80-120px vertical.
- Section padding (mobile): 48-64px vertical.
- Horizontal page padding: 24px mobile, 40-64px desktop.
- **Mobile pages MUST add `xl` (48px) bottom padding** to clear the
  floating bottom-dock navigation.

---

## 4. Surfaces and Elevation

### 4.1 Backgrounds

- Default page background: `--lpa-surface` (#FCF9F8, warm white).
- Alternate sections: `--lpa-surface-container-low` (#F6F3F2) or a
  masked `--lpa-secondary-fixed-dim` (#B9CDA4) at 15-20 percent opacity
  as a "soft organic blob".
- Avoid full-page heavy accent backgrounds. Keep accents to bands or
  small hero regions.

### 4.2 Cards

```css
.lpa-card {
  background: var(--lpa-surface-container-lowest);   /* #FFFFFF */
  border-radius: 1rem;                                /* 16px */
  padding: 1.5rem;                                    /* 24px */
  transition: transform 0.3s ease, box-shadow 0.3s ease;
  /* NO BORDER. Depth comes from surface tiers and ambient shadow. */
}

.lpa-card--hover:hover {
  transform: translateY(-2px);
  box-shadow: var(--lpa-cloud-shadow);
}

.lpa-card--feature {
  background: var(--lpa-surface-container);          /* #F0EDED */
  border-radius: 1.5rem;                              /* 24px */
  padding: 2rem;                                      /* 32px */
}
```

- **No borders.** Never `border: 1px solid ...` on cards.
- Corner radius: 1rem (default), 1.5rem (feature), 2rem (hero).
- Place a "soft organic blob" (SVG or masked div using
  `--lpa-secondary-fixed-dim` at 20 percent opacity) partially behind
  card content to break symmetry.

### 4.3 Ambient Shadows ("Cloud Shadow")

Only for elements that legitimately float: modals, primary CTAs on
scroll, bottom-dock nav, floating action buttons.

```css
--lpa-cloud-shadow: 0 12px 32px rgba(28, 27, 27, 0.06);
--lpa-cloud-shadow-lift: 0 20px 60px rgba(28, 27, 27, 0.05);
```

Avoid traditional drop shadows with tight offsets and dark opacity --
they break the "Sanctuary" atmosphere.

### 4.4 Ghost Border Fallback

If a border is required for accessibility or affordance:

```css
.lpa-ghost-border {
  border: 1px solid color-mix(in oklch, var(--lpa-outline-variant) 20%, transparent);
}
```

Never use `--lpa-outline` (#75786E) at full opacity -- it breaks the
Sanctuary vibe with mechanical geometry.

---

## 5. Core UI Components

### 5.1 Buttons

All buttons use the **pill shape** (`border-radius: 9999px`). Minimum
height on mobile is 56px with a 48px tap-target safe area.

#### 5.1.1 Primary Button (gradient)

```css
.lpa-btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 56px;
  padding: 1rem 2rem;
  background: linear-gradient(
    135deg,
    var(--lpa-primary) 0%,
    var(--lpa-primary-container) 100%
  );
  color: var(--lpa-on-primary);
  border: none;
  border-radius: 9999px;
  font-family: var(--lpa-font-label);
  font-size: 0.75rem;         /* Label-MD */
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.lpa-btn-primary:hover {
  box-shadow: var(--lpa-cloud-shadow);
}

.lpa-btn-primary:active {
  transform: scale(0.98);
}

.lpa-btn-primary:focus-visible {
  outline: 2px solid var(--lpa-secondary);
  outline-offset: 3px;
}
```

#### 5.1.2 Secondary Button (container fill)

```css
.lpa-btn-secondary {
  background: var(--lpa-secondary-container);
  color: var(--lpa-on-secondary-container);
  border: none;
  border-radius: 9999px;
  min-height: 56px;
  padding: 1rem 2rem;
  font: inherit;               /* Label-MD uppercase, same as primary */
}

.lpa-btn-secondary:hover {
  background: var(--lpa-secondary-fixed);
}
```

#### 5.1.3 Text / Ghost Button

- No background, no border.
- Text color: `var(--lpa-primary)` or `var(--lpa-on-surface)`.
- Hover: underline appears, text color transitions to
  `var(--lpa-secondary)`.

Guidelines:

- Only **one primary button per view or card**.
- Secondary and ghost are for alternative or lower-priority actions.
- All buttons must have a visible focus-visible state.

### 5.2 Inputs and Forms

Two styles are permitted: **underline-only** (preferred) and
**filled** (for dense forms). No 4-sided borders.

#### 5.2.1 Underline Input

```css
.lpa-input-underline {
  width: 100%;
  background: transparent;
  border: none;
  border-bottom: 1px solid color-mix(
    in oklch,
    var(--lpa-outline-variant) 40%,
    transparent
  );
  padding: 0.75rem 0;
  font-family: var(--lpa-font-body);
  font-size: 1rem;
  color: var(--lpa-on-surface);
  transition: border-color 0.2s ease;
}

.lpa-input-underline:focus-visible {
  outline: none;
  border-bottom: 2px solid var(--lpa-secondary);
}

.lpa-input-underline::placeholder {
  color: var(--lpa-on-surface-variant);
}
```

#### 5.2.2 Filled Input

```css
.lpa-input-filled {
  width: 100%;
  background: var(--lpa-surface-container-high);
  border: none;
  border-radius: 0.5rem;       /* 8px */
  padding: 1rem 1rem 0.5rem;
  font-family: var(--lpa-font-body);
  font-size: 1rem;
  color: var(--lpa-on-surface);
}

.lpa-input-filled:focus-visible {
  outline: 2px solid var(--lpa-secondary);
  outline-offset: 0;
}
```

#### 5.2.3 Labels and Errors

- Floating labels preferred for filled inputs; static labels above for
  underline inputs.
- Label font: Manrope `Label-SM` (0.6875rem), weight 500, color
  `var(--lpa-on-surface-variant)`, 8px above input.
- Error text: 0.8125rem, color `#B64949`, 4px below input. Link to
  input via `aria-describedby` and set `aria-invalid="true"`.
- Use `<label for>` for each input. No implicit labels.

### 5.3 Navigation

v2.0 ships **dual navigation** -- desktop uses a sticky glassmorphism
top header; mobile uses a floating bottom-dock "Sanctuary Bar".

#### 5.3.1 Desktop Header (sticky, glassmorphism)

```css
.lpa-header {
  position: sticky;
  top: 0;
  height: 80px;
  padding: 0 2.5rem;
  background: color-mix(in oklch, var(--lpa-surface) 80%, transparent);
  backdrop-filter: blur(20px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  z-index: 100;
}

.lpa-header--scrolled {
  box-shadow: var(--lpa-cloud-shadow);
}
```

- Logo: left side, height 40-50px.
- Nav items: center; uppercase `Label-MD` font, weight 500,
  `letter-spacing: 0.08em`, padding 8-12px per item.
- Right side: LanguageSwitcher + primary CTA.
- Active nav item: color transitions to `--lpa-secondary`, with a 2px
  bottom accent bar using the same color.
- Hover: color transitions to `--lpa-secondary`.

#### 5.3.2 Mobile Bottom-Dock ("Sanctuary Bar")

```css
.lpa-bottom-dock {
  position: fixed;
  bottom: 1.5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background: color-mix(in oklch, var(--lpa-surface) 80%, transparent);
  backdrop-filter: blur(20px);
  border-radius: 9999px;
  box-shadow: var(--lpa-cloud-shadow);
  z-index: 100;
}

.lpa-bottom-dock__item {
  min-width: 48px;
  min-height: 48px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  color: var(--lpa-on-surface-variant);
  font: 500 0.6875rem var(--lpa-font-label);  /* Label-SM */
  text-transform: uppercase;
  letter-spacing: 0.08em;
}

.lpa-bottom-dock__item[aria-current="page"] {
  color: var(--lpa-secondary);
}
```

- 2px stroke icons (line style, rounded caps).
- Min 48px tap target per item.
- Content scrolls behind the dock; pages must add `xl` (48px) bottom
  padding.

#### 5.3.3 Mobile Top Header + Drawer

On mobile, the top header shows only the logo and a hamburger button
(for "menu"). The hamburger opens a full-screen overlay drawer with
stacked nav links at 32px vertical spacing and 48px min tap height.
The bottom dock remains persistent behind the drawer overlay.

### 5.4 Modals and Overlays

```css
.lpa-modal-overlay {
  position: fixed;
  inset: 0;
  background: color-mix(in oklch, var(--lpa-surface) 80%, transparent);
  backdrop-filter: blur(40px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
}

.lpa-modal-card {
  background: var(--lpa-surface-container-lowest);
  border-radius: 1.5rem;       /* 24px */
  padding: 2rem;
  max-width: min(560px, 92vw);
  box-shadow: var(--lpa-cloud-shadow-lift);
}
```

- ESC closes. Click outside overlay closes.
- Focus trap: first focusable element receives focus on open; focus
  returns to the trigger element on close.
- `role="dialog"`, `aria-modal="true"`, `aria-labelledby={titleId}`,
  `aria-describedby={descId}`.
- Portal-rendered to `document.body`.

### 5.5 Chips and Badges

```css
.lpa-chip {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.75rem;
  background: var(--lpa-secondary-container);
  color: var(--lpa-on-secondary-container);
  border-radius: 9999px;
  font: 500 0.75rem var(--lpa-font-label);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
```

Variants:

- `primary` -- `var(--lpa-primary-container)` fill
- `secondary` -- `var(--lpa-secondary-container)` fill (default)
- `tertiary` -- `var(--lpa-tertiary-container)` fill
- `outline` -- transparent fill, ghost border

Chips feel like small, smooth pebbles. No borders, no icons larger
than 16px.

---

## 6. Iconography

- **Style:** line icons, stroke 2px, rounded caps and joins.
- **Palette:** monochrome `var(--lpa-on-surface)` by default;
  `var(--lpa-secondary)` for emphasis.
- **Sizes:**
  - 20-24px in text and small UI
  - 24-32px in bottom-dock nav items
  - 32-48px in feature sections and hero illustrations
- All icons come from a single family. Suggested: Lucide
  (`npm install lucide-react`) -- it has consistent 2px stroke and
  rounded caps that match the Sanctuary aesthetic.

---

## 7. Imagery and Graphics

### 7.1 Photography

- Bright, natural light. Clean studios, minimal clutter.
- Clothing in neutral shades: black, white, grey, beige, sage.
- Focus on precise Pilates form, controlled movement, calm expressions.
- Color grading: soft and slightly warm, low saturation. Avoid neon
  colors, busy gyms, and generic "hardcore fitness" imagery.
- Allow images to **break the container** -- an image might be 60
  percent of the screen width while text sits in the remaining 40
  percent with a slight overlap, creating a "layered paper" effect.

### 7.2 Graphic Elements

- **Thin curved lines** inspired by the logo stroke.
- **Soft organic blobs** using `var(--lpa-secondary-fixed-dim)` or
  `var(--lpa-tertiary-fixed-dim)` at 15-20 percent opacity. Position
  behind photos or sections as decorative context, not as overpowering
  background.
- **Fluid containers** -- SVG masks with irregular hand-drawn edges
  used to hold secondary imagery.

---

## 8. Motion and Interaction

Motion should feel like **breathing**: slow, subtle, non-distracting.

Guidelines:

- Hover transitions: 0.2-0.3s ease-out.
- Scroll-in animations: fade + 20-40px translate-up; duration 0.4-0.6s.
- Button press feedback: quick `transform: scale(0.98)` then back.
- Card hover: 2-4px lift + Cloud Shadow.
- Never use complex parallax, rapid flashes, or seizure-risk motion.
- **`prefers-reduced-motion: reduce` is mandatory.** Disable all
  transforms and transitions when the user has requested reduced
  motion:

```css
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

---

## 9. Tailwind Mapping

```ts
// frontend/tailwind.config.ts (excerpt)
import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        lpa: {
          // Brand anchors
          ink:    "#1A1A1A",
          sage:   "#9CAF88",
          beige:  "#E8DCC4",
          canvas: "#FCF9F8",

          // Material token set (Sage & Canvas snapshot)
          surface:                     "#FCF9F8",
          "surface-bright":            "#FCF9F8",
          "surface-dim":               "#DCD9D9",
          "surface-container-lowest":  "#FFFFFF",
          "surface-container-low":     "#F6F3F2",
          "surface-container":         "#F0EDED",
          "surface-container-high":    "#EAE7E7",
          "surface-container-highest": "#E5E2E1",
          "surface-variant":           "#E5E2E1",

          primary:                     "#5F5E5E",
          "primary-container":         "#AAA8A8",
          "primary-fixed":             "#E5E2E1",
          "primary-fixed-dim":         "#C8C6C5",
          "on-primary":                "#FFFFFF",
          "on-primary-container":      "#3E3D3D",
          "on-primary-fixed":          "#1C1B1B",
          "on-primary-fixed-variant":  "#474746",

          secondary:                   "#526442",
          "secondary-container":       "#D2E6BC",
          "secondary-fixed":           "#D5E9BF",
          "secondary-fixed-dim":       "#B9CDA4",
          "on-secondary":              "#FFFFFF",
          "on-secondary-container":    "#576846",
          "on-secondary-fixed":        "#111F05",
          "on-secondary-fixed-variant":"#3B4C2C",

          tertiary:                    "#665E4B",
          "tertiary-container":        "#B2A892",
          "tertiary-fixed":            "#EDE1C9",
          "tertiary-fixed-dim":        "#D1C5AE",
          "on-tertiary":               "#FFFFFF",
          "on-tertiary-container":     "#443D2C",
          "on-tertiary-fixed":         "#211B0C",
          "on-tertiary-fixed-variant": "#4D4634",

          error:                       "#BA1A1A",
          "error-container":           "#FFDAD6",
          "on-error":                  "#FFFFFF",
          "on-error-container":        "#93000A",

          "on-background":             "#1C1B1B",
          "on-surface":                "#1C1B1B",
          "on-surface-variant":        "#44483F",
          outline:                     "#75786E",
          "outline-variant":           "#C5C8BC",
          "surface-tint":              "#5F5E5E",

          "inverse-surface":           "#313030",
          "inverse-on-surface":        "#F3F0EF",
          "inverse-primary":           "#C8C6C5",
        },
      },
      borderRadius: {
        card:    "1rem",      // 16px default cards
        "card-md": "1.5rem",  // 24px feature cards
        "card-lg": "2rem",    // 32px hero cards
        pill:    "9999px",
      },
      boxShadow: {
        cloud:      "0 12px 32px rgba(28,27,27,0.06)",
        "cloud-lift": "0 20px 60px rgba(28,27,27,0.05)",
      },
      backdropBlur: {
        nav:   "20px",
        modal: "40px",
      },
      fontFamily: {
        display:  ["var(--font-epilogue)", "Cormorant Garamond", "Georgia", "serif"],
        headline: ["var(--font-epilogue)", "Cormorant Garamond", "Georgia", "serif"],
        body:     ["var(--font-manrope)",  "Inter", "system-ui", "sans-serif"],
        label:    ["var(--font-manrope)",  "Inter", "system-ui", "sans-serif"],
      },
      fontSize: {
        "display-lg":  ["3.5rem",    { lineHeight: "1.1",  letterSpacing: "-0.02em" }],
        "display-md":  ["2.75rem",   { lineHeight: "1.1",  letterSpacing: "-0.02em" }],
        "headline-lg": ["2.25rem",   { lineHeight: "1.15", letterSpacing: "-0.01em" }],
        "headline-md": ["1.75rem",   { lineHeight: "1.2",  letterSpacing: "-0.01em" }],
        "title-lg":    ["1.375rem",  { lineHeight: "1.3" }],
        "body-lg":     ["1rem",      { lineHeight: "1.6" }],
        "body-md":     ["0.875rem",  { lineHeight: "1.5" }],
        "label-md":    ["0.75rem",   { lineHeight: "1.4",  letterSpacing: "0.05em" }],
        "label-sm":    ["0.6875rem", { lineHeight: "1.35", letterSpacing: "0.08em" }],
      },
      spacing: {
        // Semantic aliases on top of Tailwind's default 4-based scale
        "lpa-xs":   "0.5rem",   //  8px
        "lpa-s":    "1rem",     // 16px
        "lpa-m":    "1.5rem",   // 24px
        "lpa-l":    "2rem",     // 32px
        "lpa-xl":   "3rem",     // 48px
        "lpa-xxl":  "4rem",     // 64px
        "lpa-xxxl": "6rem",     // 96px
      },
    },
  },
};

export default config;
```

Font loading lives in `frontend/src/app/layout.tsx`:

```ts
import { Epilogue, Manrope } from "next/font/google";

const epilogue = Epilogue({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-epilogue",
  display: "swap",
});

const manrope = Manrope({
  subsets: ["latin", "latin-ext"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-manrope",
  display: "swap",
});

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="lv" className={`${epilogue.variable} ${manrope.variable}`}>
      <body className="font-body bg-lpa-surface text-lpa-on-surface">{children}</body>
    </html>
  );
}
```

Both fonts have Latin Extended subsets covering Latvian diacritics.

---

## 10. Implementation Checklist

When building new UI:

1. **Use tokens only.** Reference `lpa-*` Tailwind classes or
   `--lpa-*` CSS variables. Never introduce ad-hoc hex codes.
2. **No 1px section borders.** Use surface tiers for depth. Ghost
   Border fallback only for affordance-critical lines (focused inputs).
3. **Mobile-first.** Start every component at 390px width; progressively
   enhance for tablet and desktop.
4. **Mobile bottom-dock clearance.** Every mobile page adds
   `pb-lpa-xl` (48px) to avoid Sanctuary Bar overlap.
5. **Typography:**
   - body text at least 16px
   - max paragraph width 60-75 characters
   - Epilogue for display and headline only
   - Manrope for everything else
6. **Buttons and forms:**
   - pill-shaped (border-radius: 9999px)
   - minimum 56px height on mobile, 48px safe-area tap target
   - visible `:focus-visible` outline (sage) at 2px offset 3px
7. **Motion:**
   - transitions 0.2-0.3s ease-out
   - card hover: 2-4px lift + Cloud Shadow
   - button press: `transform: scale(0.98)`
   - respect `prefers-reduced-motion: reduce`
8. **Accessibility:**
   - WCAG 2.2 AA contrast (4.5:1 text, 3:1 large text)
   - keyboard-reachable all interactive elements
   - `aria-*` attributes on forms, modals, nav
   - `<label for>` on every input
9. **Layout:**
   - 1200-1280px max content width (desktop)
   - 24-32px gutters
   - 80-120px vertical section spacing (desktop)
   - 48-64px vertical section spacing (mobile)
10. **Logo and imagery:**
    - respect clear space and minimum-size rules
    - use soft organic blobs for decoration, not as primary content

This document is the single source of truth for LPA web visual
implementation. Any deviations must be explicit and documented as a
new version.

---

## 11. Source of Truth and Iteration

The live visual design is maintained in **Google Stitch project
`2147031711425332256`** ("Mobile-First App Redesign"), owner Janis,
created 2026-04-08.

Active design system: **"Sage & Canvas"**.

Alternate systems stored on the project (not currently active):

- **"Etheric Flow" v1** -- Newsreader + Manrope, warmer canvas
  (#FAF9F5), "Editorial Sanctuary" variant
- **"Etheric Flow" v2** -- Newsreader + Manrope, slightly different
  secondary palette, "Ink & Canvas Sanctuary" variant

Relevant Stitch screens (by ID; fetchable via
`mcp__stitch__get_screen`):

- "LPA Homepage (Desktop)" -- hero + glassmorphism header reference
- "LPA Homepage (Refined)" -- mobile hero + bottom-dock reference
- "Trainings Catalogue (Desktop)" -- desktop card grids
- "Trainings Catalogue (Refined)" -- mobile card grids + filters
- "Membership Plans (Desktop)" -- pricing card layout
- "Membership Plans (Refined)" -- mobile pricing
- "Directory (Desktop Refined)" -- search + profile cards
- "Directory (Refined)" -- mobile directory
- "Member Dashboard (Desktop Refined)" -- signed-in layout
- "Member Dashboard (Refined)" -- mobile dashboard

### How to update this document

1. Iterate the design in Stitch. If significant visual changes ship
   (new tokens, new fonts, new navigation pattern, new component), do
   not merge frontend work based on them until the doc is updated.
2. Open this file and bump the version (2.0 -> 2.1 for minor token
   tweaks, 2.0 -> 3.0 for a new active design system).
3. Update the affected sections (1 / 2 / 4 / 5 / 9 typically).
4. Append an entry to Section 12 (Revision History) with the date and
   short summary.
5. Update `planning/phase-NN-*/PLAN.md` for any Phase whose UI work
   depends on the changed tokens.

### Offline fallback

If Stitch project access is lost (API key revoked, project deleted),
the token set in Section 1.2 and the component specs in Sections 4-5
are **sufficient by themselves** to rebuild the design system. Stitch
screens are visual reference material, not hard dependencies.

---

## 12. Revision History

### v2.0 -- 2026-04-09

**Reconciled with Stitch "Sage & Canvas".** Breaking changes:

- **Fonts:** Songer + Montserrat + Winterlady -> **Epilogue + Manrope**
  (both Google Fonts via `next/font/google`). Songer and Winterlady are
  dropped entirely; Montserrat is replaced by Manrope.
- **Color tokens:** flat `--lpa-ink/canvas/sage/mint/beige/taupe`
  (10 tokens) -> **Material Design 3 token set** (~40 tokens) with
  four brand anchor aliases retained (`--lpa-ink`, `--lpa-sage`,
  `--lpa-beige`, `--lpa-canvas`).
- **Borders:** 1px card + input borders -> **"No-Line Rule"**. Depth
  now expressed through surface tiers and Cloud Shadow.
- **Navigation:** sticky 80-96px top header -> **dual pattern**
  (desktop sticky glassmorphism header + mobile floating bottom-dock
  "Sanctuary Bar").
- **Cards:** `border-radius: 12px` with border + shadow -> `1rem`
  (DEFAULT) / `1.5rem` (md) / `2rem` (lg) with no border and optional
  Cloud Shadow on hover/lift.
- **Inputs:** full-border 4px radius -> **underline-only** (preferred)
  or **filled** (surface-container-high).
- **Type scale:** px-based desktop scale -> rem-based mobile-first
  scale with Label-MD uppercase + tracking conventions.
- **Glassmorphism + gradient textures** introduced for floating
  elements and primary CTAs.
- **Orientation:** responsive-web desktop-first -> **mobile-first**.

Non-breaking changes:

- Section 0 (Brand Assets) preserved.
- Section 3 (Layout and Spacing) preserved; breakpoints and spacing
  scale unchanged. Mobile-first preference added as a note.
- Section 6 (Iconography) preserved with Lucide recommendation.
- Section 7 (Imagery and Graphics) expanded with organic blobs and
  fluid containers.
- Section 8 (Motion) expanded with `prefers-reduced-motion` mandate.

Reason for the rewrite: the user iterated visual designs in Google
Stitch project `2147031711425332256` on 2026-04-08, producing a
polished mobile-first design system ("Sage & Canvas") that materially
diverged from doc v1.0. v2.0 snapshots Stitch as the canonical live
source of truth.

### v1.0 -- initial

Songer / Montserrat / Winterlady font stack, flat `--lpa-*` token
table, border-style cards, sticky top header navigation. Never
executed against real code -- superseded by v2.0 before Phase 01
shipped any frontend work.
