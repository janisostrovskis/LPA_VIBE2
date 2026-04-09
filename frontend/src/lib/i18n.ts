import { readFile } from "node:fs/promises";
import path from "node:path";

export const locales = ["lv", "en", "ru"] as const;
export const defaultLocale = "lv" as const;

export type Locale = (typeof locales)[number];

export class LocaleLoadError extends Error {
  constructor(locale: Locale, cause: unknown) {
    super(
      `Failed to load locale file for "${locale}": ${cause instanceof Error ? cause.message : String(cause)}`,
    );
    this.name = "LocaleLoadError";
  }
}

export async function getMessages(
  locale: Locale,
): Promise<Record<string, unknown>> {
  const filePath = path.join(
    process.cwd(),
    "public",
    "locales",
    locale,
    "common.json",
  );

  let raw: string;
  try {
    raw = await readFile(filePath, "utf-8");
  } catch (cause) {
    throw new LocaleLoadError(locale, cause);
  }

  let parsed: unknown;
  try {
    parsed = JSON.parse(raw) as unknown;
  } catch (cause) {
    throw new LocaleLoadError(locale, `JSON parse error — ${String(cause)}`);
  }

  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new LocaleLoadError(locale, "locale file must be a JSON object");
  }

  return parsed as Record<string, unknown>;
}
