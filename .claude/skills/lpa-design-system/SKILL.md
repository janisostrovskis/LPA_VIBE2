---
name: lpa-design-system
description: LPA design tokens, component specs, typography, spacing, and WCAG accessibility requirements. For Frontend Agent.
disable-model-invocation: true
user-invocable: false
---

# LPA Design System Reference

Source of truth: `docs/LPA_DESIGN_LANGUAGE.MD`

## Color Tokens (Tailwind classes)

| Token | Hex | Tailwind | Usage |
|-------|-----|----------|-------|
| `--lpa-ink` | #1A1A1A | `text-lpa-ink`, `bg-lpa-ink` | Main text, headings, nav links |
| `--lpa-canvas` | #FFFFFF | `bg-lpa-canvas` | Page background |
| `--lpa-canvas-soft` | #F8F8F8 | `bg-lpa-canvas-soft` | Alternating sections |
| `--lpa-text-secondary` | #4A4A4A | `text-lpa-text-secondary` | Secondary text, labels |
| `--lpa-text-tertiary` | #8A8A8A | `text-lpa-text-tertiary` | Captions, placeholders |
| `--lpa-border-light` | #E2E2E2 | `border-lpa-border-light` | Card/input borders |
| `--lpa-accent-sage` | #9CAF88 | `bg-lpa-accent-sage` | Primary CTAs, active states |
| `--lpa-accent-mint` | #E8F4F0 | `bg-lpa-accent-mint` | Info pills, focus rings |
| `--lpa-accent-beige` | #E8DCC4 | `bg-lpa-accent-beige` | Background blobs (low opacity) |
| `--lpa-accent-taupe` | #C9B8A8 | `bg-lpa-accent-taupe` | Secondary borders, muted tags |

**Rule:** 70-80% neutral, 20-30% accents. Max 2 accent colors per component. No ad-hoc hex codes.

## Typography

| Role | Font | Size | Weight | Tailwind |
|------|------|------|--------|----------|
| Display/H0 | Songer | 64px | 400-700 | `font-display text-[64px]` |
| H1 | Songer | 48px | 500-700 | `font-display text-5xl` |
| H2 | Songer/Montserrat | 36px | 500-700 | `font-display text-4xl` |
| H3 | Montserrat | 28px | 500 | `font-ui text-3xl` |
| H4 | Montserrat | 22px | 500 | `font-ui text-xl` |
| Body L | Montserrat | 18px | 400 | `font-ui text-lg` |
| Body | Montserrat | 16px | 400 | `font-ui text-base` |
| Caption | Montserrat | 13-14px | 400-500 | `font-ui text-sm` |

**Winterlady** (script font): ONLY for 1-2 accent words near headings. NEVER in nav, body, forms, or buttons.

## Spacing (8px scale)

| Token | Value | Usage |
|-------|-------|-------|
| xs | 8px / `p-2` | Icon gaps |
| s | 16px / `p-4` | Label to input |
| m | 24px / `p-6` | Card inner padding |
| l | 32px / `p-8` | Card margins |
| xl | 48px / `py-12` | Section spacing (mobile) |
| xxl | 64px / `py-16` | Section padding (desktop) |
| xxxl | 96px / `py-24` | Hero padding |

## Components

### Buttons
- **Primary:** `rounded-full bg-lpa-accent-sage text-white px-8 py-3.5 uppercase tracking-wider text-sm font-medium`
- **Secondary:** `rounded-full border-[1.5px] border-lpa-ink text-lpa-ink px-8 py-3.5 uppercase tracking-wider text-sm font-medium`
- **Ghost:** No border, transparent. Text underline on hover, color → sage.
- **Rule:** ONE primary button per view/card.

### Cards
- `rounded-xl border border-lpa-border-light shadow-card p-6`
- Hover: `hover:shadow-card-hover hover:-translate-y-0.5`
- Variants: "ghost" (border only), "feature" (mint background at low opacity)

### Inputs
- `rounded border border-[#d4d4d4] px-4 py-3 text-base w-full`
- Focus: `focus:border-lpa-accent-sage focus:ring-[3px] focus:ring-lpa-accent-sage/16`
- Error: `border-[#b64949]` with error text in `text-[#b64949] text-sm mt-1`
- Always use `<label>` with `htmlFor`. Always `aria-invalid` + `aria-describedby` for errors.

### Navigation
- Height: 80-96px. Background: white with 98% opacity.
- On scroll: subtle shadow `shadow-[0_2px_8px_rgba(0,0,0,0.04)]`
- Links: `uppercase tracking-wider text-sm font-medium`
- Active: sage color + bottom border
- Mobile: slide-in drawer, 48px min tap targets, 32px vertical spacing

## Motion

- Hover transitions: `transition-all duration-200 ease-out`
- Scroll-in: fade + translateY(20-40px), duration 400-600ms
- Card hover: lift 2-4px + stronger shadow
- Button click: quick scale to 0.98
- **Feel like "breathing" — slow, subtle, non-distracting**

## WCAG 2.2 AA Checklist

- [ ] Body text minimum 16px
- [ ] Color contrast ratio 4.5:1 for normal text, 3:1 for large text
- [ ] All interactive elements have visible focus states (outline or ring)
- [ ] All form inputs have associated `<label>` elements
- [ ] Error messages use `aria-invalid` and `aria-describedby`
- [ ] Images have meaningful `alt` text
- [ ] Keyboard navigation works on all interactive elements (Tab, Enter, Escape)
- [ ] No content conveyed by color alone
- [ ] Skip-to-content link on every page
- [ ] Headings follow hierarchy (h1 → h2 → h3, no skipping)

## Layout

- Max width: 1280px (`max-w-7xl`)
- Grid: 12 columns desktop, 8 tablet, 4 mobile
- Gutters: 24-32px (`gap-6` or `gap-8`)
- Breakpoints: `sm:` 640px, `md:` 768px, `lg:` 1024px, `xl:` 1440px
