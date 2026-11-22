import path from "node:path";

import { expect, test } from "@playwright/test";

const SAMPLE = path.resolve(__dirname, "../../../services/api/tests/ingest/fixtures/sample.vtt");

test("approve Gate 1, then read the architecture: diagram, cost total, cards on a phone", async ({ page }) => {
  await page.goto("/runs/new");
  await page.getByTestId("file-input").setInputFiles(SAMPLE);
  await page.getByLabel("Client name").fill("Kestrel Freight Co.");
  await page.getByRole("button", { name: "Start run" }).click();
  await expect(page).toHaveURL(/\/runs\/r_[0-9a-f]{6}$/);
  await expect(page.locator('.gate[data-gate="gate1"]')).toHaveAttribute("data-view", "waiting");

  await page.getByRole("link", { name: "Brief", exact: true }).click();
  await page.getByRole("region", { name: "Gate 1 decision" }).getByRole("button", { name: "Approve brief" }).click();
  await expect(page.getByText("Brief approved", { exact: true })).toBeVisible();
  await expect(page).toHaveURL(/\/runs\/r_[0-9a-f]{6}$/); // the approve redirect lands first

  await page.getByRole("link", { name: "Architecture", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Architecture spec" })).toBeVisible();
  await expect(page.getByTestId("diagram").locator("svg")).toBeVisible();
  await expect(page.getByTestId("use-case")).toBeVisible();
  const costRow = page.locator("tr", { hasText: "Total" });
  await expect(costRow).toContainText("$45.00");
  await expect(page.getByRole("link", { name: "Download .md" })).toBeVisible();

  await page.setViewportSize({ width: 375, height: 800 });
  await expect(page.locator(".table.cards thead").first()).toBeHidden();
  await expect(costRow.locator("td").first()).toHaveCSS("display", "flex");
  const overflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(overflow).toBeLessThanOrEqual(0);
});
