import { expect, test } from "@playwright/test";

// The list is stubbed empty, so other specs may create runs in the same database.
test("empty database shows the first-run state", async ({ page }) => {
  await page.route("**/api/runs", (route) => route.fulfill({ json: [] }));
  await page.goto("/");
  await expect(page.getByText("Start your first run")).toBeVisible();
});
