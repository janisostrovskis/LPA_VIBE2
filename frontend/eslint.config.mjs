import { FlatCompat } from "@eslint/eslintrc";
import tsParser from "@typescript-eslint/parser";
import { fileURLToPath } from "url";
import path from "path";

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

/** @type {import('eslint').Linter.Config[]} */
const eslintConfig = [
  // Ignores must come first in flat config (global ignores block).
  {
    ignores: [
      ".next/",
      "node_modules/",
      "playwright-report/",
      "test-results/",
      "next-env.d.ts",
      // Config files run in a plain Node context — type-aware linting is
      // unnecessary and would require adding them to tsconfig.json.
      "*.config.{js,mjs,cjs,ts}",
      "postcss.config.mjs",
    ],
  },

  ...compat.extends("next/core-web-vitals", "next/typescript"),

  // Type-aware rules only on actual TypeScript source, where parser services
  // can be resolved from tsconfig.json. `no-floating-promises` requires this.
  {
    files: ["src/**/*.{ts,tsx}", "tests/**/*.{ts,tsx}"],
    languageOptions: {
      parser: tsParser,
      parserOptions: {
        projectService: true,
        tsconfigRootDir: __dirname,
      },
    },
    rules: {
      "no-empty": ["error", { allowEmptyCatch: false }],
      "@typescript-eslint/no-floating-promises": "error",
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/ban-ts-comment": "error",
    },
  },

  // Baseline rules for any file the typed block doesn't cover.
  {
    rules: {
      "no-empty": ["error", { allowEmptyCatch: false }],
    },
  },
];

export default eslintConfig;
