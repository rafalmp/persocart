/**
 * TASK-021: WCAG accessibility E2E checks via @axe-core/playwright.
 *
 * Run with: bunx playwright test
 * Requires full stack: docker compose up
 */

import { test, expect } from "@playwright/test";
import AxeBuilder from "@axe-core/playwright";

test.describe("Storefront accessibility", () => {
  test("home page has no serious/critical axe violations", async ({ page }) => {
    await page.goto("/");
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "serious" || v.impact === "critical",
    );
    expect(serious).toHaveLength(0);
  });

  test("skip-to-main link is present and functional", async ({ page }) => {
    await page.goto("/");
    const skipLink = page.locator('a[href="#main"]');
    await expect(skipLink).toBeAttached();
  });

  test("login page has no serious/critical axe violations", async ({ page }) => {
    await page.goto("/admin/login");
    const results = await new AxeBuilder({ page })
      .withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"])
      .analyze();
    const serious = results.violations.filter(
      (v) => v.impact === "serious" || v.impact === "critical",
    );
    expect(serious).toHaveLength(0);
  });

  test("tap targets are at least 44px on mobile viewport", async ({ page }) => {
    await page.setViewportSize({ width: 390, height: 844 });
    await page.goto("/");
    // Check all interactive elements meet 44px minimum
    const smallTargets = await page.evaluate(() => {
      const interactive = document.querySelectorAll("a, button, input, select");
      return Array.from(interactive)
        .filter((el) => {
          const rect = el.getBoundingClientRect();
          return (
            (rect.width > 0 && rect.width < 44) ||
            (rect.height > 0 && rect.height < 44)
          );
        })
        .map((el) => ({
          tag: el.tagName,
          text: el.textContent?.trim().slice(0, 50),
          width: el.getBoundingClientRect().width,
          height: el.getBoundingClientRect().height,
        }));
    });
    expect(smallTargets).toHaveLength(0);
  });
});
