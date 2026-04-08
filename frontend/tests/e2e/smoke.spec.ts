import { test, expect } from "@playwright/test";

test("home page loads Latvian", async ({ page }) => {
  await page.goto("/lv");
  await expect(page.locator("h1")).toContainText("Latvijas Pilates");
});
