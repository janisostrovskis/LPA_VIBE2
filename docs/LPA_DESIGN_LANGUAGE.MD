````markdown
# Latvijas Pilates Asociācija Web Design Stylebook

Version: 1.0  
Owner: LPA / Janis  
Last updated: YYYY-MM-DD

This document defines the visual design system for the **Latvijas Pilates Asociācija** website and related web properties.  
It is intended for **engineers and designers** implementing UI in code (CSS/Tailwind/Design Tokens).

---

## 0. Brand Assets

- Primary logo file (line-art Pilates pose + wordmark):  
  `/mnt/data/20210618_lpa_logo_vards_zime_white_LV.png`
- Provide variants (recommended):
  - `lpa-logo-primary.svg` – dark lines on light background
  - `lpa-logo-inverse.svg` – white lines for dark backgrounds
  - `lpa-logo-mark-only.svg` – illustration only (no wordmark) for favicon / small spaces

### Logo Rules

- **Clear space:** ≥ height of the word “LPA” on all sides.
- **Minimum digital height:** 32px.
- Never:
  - distort, stretch or rotate
  - change stroke width
  - add shadows/glows/outlines
  - recolor to non-brand colors (keep monochrome / accent versions only if explicitly defined later)

---

## 1. Design Tokens

These are the canonical names. Map them to CSS variables, Tailwind config, or design system tokens.

### 1.1 Color Tokens

```css
:root {
  /* Core */
  --lpa-ink: #1a1a1a;
  --lpa-canvas: #ffffff;
  --lpa-canvas-soft: #f8f8f8;

  /* Text */
  --lpa-text-secondary: #4a4a4a;
  --lpa-text-tertiary: #8a8a8a;

  /* Neutrals */
  --lpa-border-light: #e2e2e2;
  --lpa-divider-subtle: #efefef;

  /* Accents */
  --lpa-accent-sage: #9caf88;
  --lpa-accent-mint: #e8f4f0;
  --lpa-accent-beige: #e8dcc4;
  --lpa-accent-taupe: #c9b8a8;
}
```
````

#### Color Usage

| Token                  | Hex     | Usage                                                      |
| ---------------------- | ------- | ---------------------------------------------------------- |
| `--lpa-ink`            | #1A1A1A | Logo, main headings, primary text, nav links               |
| `--lpa-canvas`         | #FFFFFF | Page background                                            |
| `--lpa-canvas-soft`    | #F8F8F8 | Alternating sections, neutral surfaces                     |
| `--lpa-text-secondary` | #4A4A4A | Secondary text, labels, muted headings                     |
| `--lpa-text-tertiary`  | #8A8A8A | Captions, meta info, placeholders                          |
| `--lpa-border-light`   | #E2E2E2 | Card borders, input borders                                |
| `--lpa-divider-subtle` | #EFEFEF | Horizontal dividers, table row separators                  |
| `--lpa-accent-sage`    | #9CAF88 | Primary CTAs, active states, key highlights                |
| `--lpa-accent-mint`    | #E8F4F0 | Info pills, soft highlights, focus ring backgrounds        |
| `--lpa-accent-beige`   | #E8DCC4 | Background blobs, subtle section backgrounds (low opacity) |
| `--lpa-accent-taupe`   | #C9B8A8 | Secondary borders, muted tags, backgrounds                 |

Guidelines:

- UI should be **mostly neutral**: 70–80% white/greys, 20–30% accents.
- Avoid using more than **2 accent colors** on a single component.
- For text on images, maintain WCAG AA contrast; add gradient overlays where needed.

---

## 2. Typography

### 2.1 Font Stacks

```css
:root {
  --lpa-font-display: "Songer", system-ui, -apple-system, sans-serif;
  --lpa-font-ui: "Montserrat", system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI",
    sans-serif;
  --lpa-font-script: "Winterlady", "Brush Script MT", cursive;
}
```

- **Display Sans:** _Songer_
  Used for large headings (hero, section titles). A modern geometric sans-serif.
  Available weights: Regular (400), Medium (500), Bold (700).
- **UI Sans:** _Montserrat_
  Used for navigation, body text, forms, buttons, labels.
- **Script Accent:** _Winterlady_
  Used only for very short accent words (1–2 words) near headings.

### 2.2 Type Scale (Desktop)

| Role           | Font              | Size    | Line-height | Weight  |
| -------------- | ----------------- | ------- | ----------- | ------- |
| Display / H0   | Songer            | 64px    | 1.1         | 400–700 |
| H1             | Songer            | 48px    | 1.15        | 500–700 |
| H2             | Songer/Montserrat | 36px    | 1.2         | 500–700 |
| H3             | Montserrat        | 28px    | 1.25        | 500     |
| H4             | Montserrat        | 22px    | 1.3         | 500     |
| Body L         | Montserrat        | 18px    | 1.6         | 400     |
| Body           | Montserrat        | 16px    | 1.6         | 400     |
| Caption / Meta | Montserrat        | 13–14px | 1.4         | 400–500 |

Mobile: scale down headings by ~2–6px (keep body at **16px min**).

### 2.3 Typographic Rules

- Max line length: ~60–75 characters for paragraphs.
- No script font in:

  - navigation
  - body text
  - forms or buttons

- Headings: usually ≤2 lines.
- UI labels / nav items may use small caps or letter-spacing `0.08–0.12em`.

---

## 3. Layout & Spacing

### 3.1 Breakpoints

You can adapt, but recommended:

```text
mobile:    0–767px
tablet:    768–1023px
desktop:   1024–1439px
wide:      1440px+
```

### 3.2 Grid

- Max content width: **1200–1280px**.
- Desktop: **12-column grid**, gutters 24–32px.
- Tablet: 8-column grid.
- Mobile: 4 columns or simple full-width.

### 3.3 Spacing Scale

Use multiples of 8:

| Token  | Value | Usage                                    |
| ------ | ----- | ---------------------------------------- |
| `xs`   | 8px   | tiny gaps, icon spacing                  |
| `s`    | 16px  | label to input, text blocks              |
| `m`    | 24px  | card inner padding                       |
| `l`    | 32px  | card margins, section inner padding      |
| `xl`   | 48px  | vertical space between sections (mobile) |
| `xxl`  | 64px  | vertical padding (desktop sections)      |
| `xxxl` | 96px  | hero padding or major separators         |

Section padding (desktop): 80–120px vertical.
Section padding (mobile): 48–64px vertical.

Horizontal page padding:

- Mobile: 24px
- Desktop: 40–64px

---

## 4. Surfaces & Elevation

### 4.1 Backgrounds

- Default page: `--lpa-canvas`.
- Alternate sections: `--lpa-canvas-soft` or `--lpa-accent-beige` at low opacity.
- Avoid full-page heavy accent backgrounds; keep them to small bands or components.

### 4.2 Cards

Base card style:

```css
.lpa-card {
  background: var(--lpa-canvas);
  border-radius: 12px;
  border: 1px solid var(--lpa-border-light);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06);
  padding: 24px;
  transition: box-shadow 0.3s ease, transform 0.3s ease;
}

.lpa-card:hover {
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}
```

- Use **border OR stronger shadow**, not both heavy at once.
- Variants:

  - “ghost” cards: no shadow, only border.
  - “feature” cards: subtle background using `--lpa-accent-mint` at low opacity.

---

## 5. Core UI Components

### 5.1 Buttons

#### Primary Button

```css
.lpa-btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--lpa-accent-sage);
  color: #ffffff;
  border-radius: 9999px;
  border: none;
  padding: 14px 32px;
  font-family: var(--lpa-font-ui);
  font-size: 15px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: background 0.25s ease, transform 0.25s ease, box-shadow 0.25s ease;
}

.lpa-btn-primary:hover {
  background: #869b7e; /* ~10% darker */
  box-shadow: 0 4px 15px rgba(156, 175, 136, 0.4);
  transform: translateY(-2px);
}

.lpa-btn-primary:active {
  transform: translateY(0);
  box-shadow: none;
}

.lpa-btn-primary:focus-visible {
  outline: 2px solid var(--lpa-accent-mint);
  outline-offset: 2px;
}
```

#### Secondary Button

```css
.lpa-btn-secondary {
  background: transparent;
  color: var(--lpa-ink);
  border-radius: 9999px;
  border: 1.5px solid var(--lpa-ink);
  padding: 14px 32px;
  font-family: var(--lpa-font-ui);
  font-size: 15px;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  cursor: pointer;
  transition: background 0.25s ease, color 0.25s ease;
}

.lpa-btn-secondary:hover {
  background: rgba(156, 175, 136, 0.08); /* subtle sage tint */
}
```

#### Text / Ghost Button

- No border, transparent background.
- Text color: `--lpa-ink`.
- Underline appears on hover, text color → `--lpa-accent-sage`.

Guidelines:

- Only one **primary** button per view or card.
- Secondary / ghost used for alternative or lower-priority actions.

---

### 5.2 Links

```css
.lpa-link {
  color: var(--lpa-ink);
  text-decoration: none;
  transition: color 0.2s ease;
}

.lpa-link:hover {
  color: var(--lpa-accent-sage);
  text-decoration: underline;
  text-underline-offset: 4px;
}
```

- In body text: no underline by default; underline on hover.
- For nav items: underline or pill background for active state.

---

### 5.3 Forms

#### Inputs

```css
.lpa-input {
  width: 100%;
  background: #ffffff;
  border: 1px solid #d4d4d4;
  border-radius: 4px;
  padding: 12px 16px;
  font-family: var(--lpa-font-ui);
  font-size: 16px;
  color: var(--lpa-ink);
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.lpa-input::placeholder {
  color: var(--lpa-text-tertiary);
}

.lpa-input:focus-visible {
  border-color: var(--lpa-accent-sage);
  outline: none;
  box-shadow: 0 0 0 3px rgba(156, 175, 136, 0.16);
}

.lpa-input--error {
  border-color: #b64949;
}

.lpa-input-hint {
  font-size: 13px;
  color: var(--lpa-text-tertiary);
  margin-top: 4px;
}

.lpa-input-error {
  font-size: 13px;
  color: #b64949;
  margin-top: 4px;
}
```

#### Labels

- Font: Montserrat 14px, weight 500.
- Color: `--lpa-text-secondary`.
- Spacing: 8px between label and input.

Accessibility:

- Use `label` with `for` attribute for each input.
- Provide `aria-invalid="true"` and `aria-describedby` for error texts.

---

### 5.4 Navigation Bar

Visual rules:

- Height: 80–96px.
- Background: `rgba(255,255,255,0.98)`.
- On scroll:

  - Add shadow: `0 2px 8px rgba(0,0,0,0.04)`.
  - Optional `backdrop-filter: blur(10px)` if performance allows.

- Logo height: 40–50px.

Menu items:

```css
.lpa-nav-link {
  font-family: var(--lpa-font-ui);
  font-size: 14px;
  font-weight: 500;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--lpa-ink);
  padding: 8px 12px;
  text-decoration: none;
  transition: color 0.2s ease;
}

.lpa-nav-link:hover {
  color: var(--lpa-accent-sage);
}

.lpa-nav-link--active {
  color: var(--lpa-accent-sage);
  border-bottom: 2px solid var(--lpa-accent-sage);
}
```

Mobile:

- Slide-in drawer or full-screen overlay.
- Background: `--lpa-canvas`.
- Links stacked with 32px vertical spacing; large tap targets (min height 48px).

---

## 6. Iconography

- Style: **line icons**, stroke 2px, rounded caps/joins.
- Palette: monochrome (`--lpa-ink`), `--lpa-accent-sage` for emphasis.
- Sizes:

  - 24px in text / small UI.
  - 32–48px in feature sections.

All icons should come from a single family (e.g. Feather, Phosphor) or consistent custom set.

---

## 7. Imagery & Graphics

### 7.1 Photography

- Bright, natural light.
- Clean studios, minimal clutter.
- Clothing in neutral shades: black, white, grey, beige.
- Focus on **precise Pilates form**, controlled movement, calm expressions.
- Adjust color grading to be **soft and slightly warm**, low saturation.

Avoid:

- Neon colors, busy gyms, generic “hardcore fitness” imagery.

### 7.2 Graphic Elements

- Use **thin curved lines** inspired by the logo.
- Soft organic blobs using:

  - `--lpa-accent-beige` and/or
  - `--lpa-accent-mint` at 10–20% opacity.

- Position behind photos or sections, not overpowering content.

---

## 8. Motion & Interaction

- Motion should feel like **breathing**: slow, subtle, non-distracting.

Guidelines:

- Hover transitions: 0.2–0.3s ease-out.
- Scroll-in animations: fade + 20–40px translate-up; duration 0.4–0.6s.
- Button click: quick scale to 0.98 then back.
- Card hover: small lift (2–4px) and stronger shadow.
- Avoid complex parallax or rapid/flashy animations.

---

## 9. Tailwind (Optional Mapping)

If using Tailwind, approximate mapping:

```js
// tailwind.config.js (excerpt)
module.exports = {
  theme: {
    extend: {
      colors: {
        lpa: {
          ink: "#1A1A1A",
          canvas: "#FFFFFF",
          "canvas-soft": "#F8F8F8",
          "text-secondary": "#4A4A4A",
          "text-tertiary": "#8A8A8A",
          "border-light": "#E2E2E2",
          "accent-sage": "#9CAF88",
          "accent-mint": "#E8F4F0",
          "accent-beige": "#E8DCC4",
          "accent-taupe": "#C9B8A8",
        },
      },
      borderRadius: {
        card: "12px",
        pill: "9999px",
      },
      boxShadow: {
        card: "0 4px 12px rgba(0,0,0,0.06)",
        "card-hover": "0 8px 24px rgba(0,0,0,0.10)",
      },
      fontFamily: {
        display: ["Cormorant Garamond", "serif"],
        ui: ["Montserrat", "system-ui", "sans-serif"],
        script: ["Allura", "cursive"],
      },
    },
  },
};
```

---

## 10. Implementation Checklist

When building new UI:

1. Use **tokens** from this file; do not introduce ad-hoc hex codes or fonts.
2. Check:

   - body text: 16px minimum
   - sufficient contrast (aim for WCAG 2.1 AA)

3. Ensure buttons and form elements:

   - use defined radii and padding
   - have focus states (keyboard accessible)

4. Keep layout:

   - 1200–1280px max width
   - 24–32px gutters
   - 80–120px vertical section spacing (desktop)

5. Respect logo rules and clear space.

This .MD file is the single source of truth for LPA web visual implementation.
Any deviations should be explicit and documented as a new version.

```

```
