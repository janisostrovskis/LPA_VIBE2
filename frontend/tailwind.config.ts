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
          ink: "#1A1A1A",
          canvas: "#FFFFFF",
          "canvas-soft": "#F8F8F8",
          "text-secondary": "#4A4A4A",
          "text-tertiary": "#8A8A8A",
          "border-light": "#E2E2E2",
          "divider-subtle": "#EFEFEF",
          "accent-sage": "#9CAF88",
          "accent-mint": "#E8F4F0",
          "accent-beige": "#E8DCC4",
          "accent-taupe": "#C9B8A8",
        },
      },
      spacing: {
        xs: "8px",
        s: "16px",
        m: "24px",
        l: "32px",
        xl: "48px",
        xxl: "64px",
        xxxl: "96px",
      },
      borderRadius: {
        card: "12px",
      },
      fontFamily: {
        songer: ["Songer", "system-ui", "serif"],
        sans: ["Montserrat", "system-ui", "sans-serif"],
        winterlady: ["Winterlady", "cursive"],
      },
    },
  },
  plugins: [],
};

export default config;
