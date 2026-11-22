import { expect, test } from "@playwright/test";

// Runs against the real dev servers (web on 3000, API on 8000) with an empty database.
test("empty database shows the first-run state", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByText("Start your first run")).toBeVisible();
});
