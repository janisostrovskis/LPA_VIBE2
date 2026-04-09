import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    screens: {
      md: "768px",
      lg: "1024px",
      xl: "1440px",
    },
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
        card:      "1rem",
        "card-md": "1.5rem",
        "card-lg": "2rem",
        pill:      "9999px",
      },
      boxShadow: {
        cloud:        "0 12px 32px rgba(28,27,27,0.06)",
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
  plugins: [],
};

export default config;
