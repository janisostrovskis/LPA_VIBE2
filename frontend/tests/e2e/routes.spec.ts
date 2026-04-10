import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const locales = ["lv", "en", "ru"] as const;

const routes = [
  { path: "", key: "home" },
  { path: "/about", key: "about" },
  { path: "/join", key: "join" },
  { path: "/trainings", key: "trainings" },
  { path: "/directory", key: "directory" },
  { path: "/news", key: "news" },
  { path: "/resources", key: "resources" },
  { path: "/verify", key: "verify" },
  { path: "/contact", key: "contact" },
  { path: "/legal/privacy", key: "privacy" },
  { path: "/legal/terms", key: "terms" },
  { path: "/legal/cookies", key: "cookies" },
];

const loadTitle = (locale: string, pageKey: string): string => {
  const p = join(process.cwd(), "public", "locales", locale, "common.json");
  const json = JSON.parse(readFileSync(p, "utf-8")) as {
    pages: Record<string, { title: string } | undefined>;
  };
  const page = json.pages[pageKey];
  if (!page) throw new Error(`Missing translation key pages.${pageKey} in ${locale}/common.json`);
  return page.title;
};

for (const locale of locales) {
  for (const route of routes) {
    test(`${locale}${route.path || "/"} returns 200 with correct h1`, async ({ page }) => {
      const response = await page.goto(`/${locale}${route.path}`);
      expect(response?.status()).toBe(200);
      const h1 = page.locator("h1").first();
      await expect(h1).toContainText(loadTitle(locale, route.key));
    });
  }
}
