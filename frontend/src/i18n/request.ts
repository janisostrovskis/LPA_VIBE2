import { notFound } from "next/navigation";
import { getRequestConfig } from "next-intl/server";
import { readFile } from "node:fs/promises";
import path from "node:path";
import { locales, type Locale } from "@/lib/i18n";

async function loadMessages(locale: Locale): Promise<Record<string, unknown>> {
  const filePath = path.join(
    process.cwd(),
    "public",
    "locales",
    locale,
    "common.json",
  );
  const raw = await readFile(filePath, "utf-8");
  const parsed: unknown = JSON.parse(raw);
  if (typeof parsed !== "object" || parsed === null || Array.isArray(parsed)) {
    throw new Error(`Locale file for "${locale}" must be a JSON object`);
  }
  return parsed as Record<string, unknown>;
}

export default getRequestConfig(async ({ requestLocale }) => {
  const requested = await requestLocale;
  const locale = (locales as readonly string[]).includes(requested ?? "")
    ? (requested as Locale)
    : undefined;
  if (!locale) notFound();
  return { locale, messages: await loadMessages(locale) };
});
