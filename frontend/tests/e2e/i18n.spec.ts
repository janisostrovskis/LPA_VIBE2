import { test, expect } from "@playwright/test";
import { readFileSync } from "node:fs";
import { join } from "node:path";

const loadSiteName = (locale: string): string => {
  const p = join(process.cwd(), "public", "locales", locale, "common.json");
  return JSON.parse(readFileSync(p, "utf-8")).site.name;
};

for (const locale of ["lv", "en", "ru"] as const) {
  test(`${locale} renders localized site name`, async ({ page }) => {
    await page.goto(`/${locale}`);
    await expect(page.getByText(loadSiteName(locale)).first()).toBeVisible();
  });
}

test("root redirects to /lv", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/lv(\/|$)/);
});
