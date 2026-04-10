import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

const locales = ["lv", "en", "ru"] as const;

const routes = [
  { path: "", label: "home" },
  { path: "/about", label: "about" },
  { path: "/join", label: "join" },
  { path: "/trainings", label: "trainings" },
  { path: "/directory", label: "directory" },
  { path: "/news", label: "news" },
  { path: "/resources", label: "resources" },
  { path: "/verify", label: "verify" },
  { path: "/contact", label: "contact" },
  { path: "/legal/privacy", label: "privacy" },
  { path: "/legal/terms", label: "terms" },
  { path: "/legal/cookies", label: "cookies" },
];

for (const locale of locales) {
  for (const route of routes) {
    test(`a11y: ${locale}${route.path || "/"} has no critical/serious violations`, async ({ page }) => {
      await page.goto(`/${locale}${route.path}`);
      await page.waitForLoadState("networkidle");

      const results = await new AxeBuilder({ page })
        .withTags(["wcag2a", "wcag2aa", "wcag22aa"])
        .analyze();

      const serious = results.violations.filter(
        (v) => v.impact === "critical" || v.impact === "serious"
      );

      if (serious.length > 0) {
        const summary = serious
          .map(
            (v) =>
              `[${v.impact}] ${v.id}: ${v.description} (${v.nodes.length} nodes)`
          )
          .join("\n");
        expect.soft(serious, `Violations found:\n${summary}`).toHaveLength(0);
      }
    });
  }
}
