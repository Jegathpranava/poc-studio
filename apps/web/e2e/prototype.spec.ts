import path from "node:path";

import { expect, test } from "@playwright/test";

const SAMPLE = path.resolve(__dirname, "../../../services/api/tests/ingest/fixtures/sample.vtt");

// The Prototype Builder runs real `npm ci` and `next build` here (no fake), then the API starts `next start`.
test.setTimeout(4 * 60_000);

test("approve Gate 1, wait for Gate 2, then see the prototype in the frame and narrow it to a phone", async ({ page }) => {
  await page.goto("/runs/new");
  await page.getByTestId("file-input").setInputFiles(SAMPLE);
  await page.getByLabel("Client name").fill("Acme Freight");
  await page.getByRole("button", { name: "Start run" }).click();
  await expect(page).toHaveURL(/\/runs\/r_[0-9a-f]{6}$/);
  await expect(page.locator('.gate[data-gate="gate1"]')).toHaveAttribute("data-view", "waiting");

  await page.getByRole("link", { name: "Brief", exact: true }).click();
  await page.getByRole("region", { name: "Gate 1 decision" }).getByRole("button", { name: "Approve brief" }).click();
  await expect(page.getByText("Brief approved", { exact: true })).toBeVisible();
  await expect(page).toHaveURL(/\/runs\/r_[0-9a-f]{6}$/);
  await expect(page.locator('.gate[data-gate="gate2"]')).toHaveAttribute("data-view", "waiting", { timeout: 3.5 * 60_000 });

  await page.getByRole("link", { name: "Prototype", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Prototype", level: 1 })).toBeVisible();
  const iframe = page.locator("iframe[title='Prototype preview']");
  await expect(iframe).toHaveAttribute("src", /^http:\/\/127\.0\.0\.1:43\d\d\/$/, { timeout: 90_000 });
  await expect(page.frameLocator("iframe[title='Prototype preview']").locator("body")).toContainText("Acme", {
    timeout: 60_000,
  });
  await expect(page.getByRole("link", { name: /Open in new tab/ })).toHaveAttribute("href", /127\.0\.0\.1:43\d\d/);
  await expect(page.getByRole("tree", { name: "Generated files" })).toContainText("package.json");
  await expect(page.getByText("Build passed")).toBeVisible();

  const device = page.getByTestId("device");
  const wide = (await device.boundingBox())?.width ?? 0;
  await page.getByRole("button", { name: "Phone" }).click();
  await expect(device).toHaveClass(/mobile/);
  await expect.poll(async () => (await device.boundingBox())?.width ?? 9999).toBeLessThan(wide);
});
