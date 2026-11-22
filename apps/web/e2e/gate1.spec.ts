import path from "node:path";

import { expect, test, type Page } from "@playwright/test";

const SAMPLE = path.resolve(__dirname, "../../../services/api/tests/ingest/fixtures/sample.vtt");

async function startRun(page: Page): Promise<string> {
  await page.goto("/runs/new");
  await page.getByTestId("file-input").setInputFiles(SAMPLE);
  await expect(page.getByText("sample.vtt")).toBeVisible();
  await page.getByLabel("Client name").fill("Kestrel Freight Co.");
  await page.getByRole("button", { name: "Sector" }).click();
  await page.getByRole("option", { name: "Logistics" }).click();
  await page.getByRole("button", { name: "Start run" }).click();
  await expect(page).toHaveURL(/\/runs\/r_[0-9a-f]{6}$/);
  await expect(page.getByText("Run started")).toBeVisible();
  return page.url().split("/").pop() ?? "";
}

async function waitForGate1(page: Page) {
  await expect(page.locator(".badge", { hasText: "Waiting at Gate 1" })).toBeVisible();
  await expect(page.locator('.gate[data-gate="gate1"]')).toHaveAttribute("data-view", "waiting");
}

test("upload, review the brief, edit the budget and approve", async ({ page }) => {
  test.setTimeout(5 * 60_000);
  await startRun(page);
  await waitForGate1(page);
  await expect(page.locator('.step[data-agent="intelligence"]')).toHaveAttribute("data-state", "done");
  await expect(page.locator(".steplog[open]")).toHaveCount(0); // logs stay collapsed

  await page.getByRole("link", { name: "Brief", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Review the brief" })).toBeVisible();
  await expect(page.getByTestId("brief-version")).toContainText("Brief v1");
  await page.getByLabel("Budget", { exact: true }).fill("About $99k");

  await page.getByRole("region", { name: "Gate 1 decision" }).getByRole("button", { name: "Approve brief" }).click();
  await expect(page.getByText("Brief approved", { exact: true })).toBeVisible();
  await expect(page).toHaveURL(/\/runs\/r_[0-9a-f]{6}$/);
  await expect(page.locator('.gate[data-gate="gate1"]')).toHaveAttribute("data-view", "passed");
  await expect(page.locator(".badge", { hasText: "Waiting at Gate 2" })).toBeVisible({ timeout: 4 * 60_000 }); // the real pipeline runs now

  await page.getByRole("link", { name: "Brief", exact: true }).click();
  await expect(page.getByTestId("brief-version")).toContainText("Brief v2");
  await expect(page.getByLabel("Budget", { exact: true })).toHaveValue("About $99k");
  await expect(page.getByText("read-only because the run is not waiting at Gate 1")).toBeVisible();
});

test("Re-extract with a note creates brief v2", async ({ page }) => {
  await startRun(page);
  await waitForGate1(page);
  await page.getByRole("link", { name: "Brief", exact: true }).click();
  await expect(page.getByTestId("brief-version")).toContainText("Brief v1");

  await page.getByRole("button", { name: "Re-extract with a note" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Note").fill("Treat the budget as unconfirmed.");
  await dialog.getByRole("button", { name: "Re-extract" }).click();

  await expect(page.getByTestId("brief-version")).toContainText("Brief v2");
  await expect(page.getByRole("button", { name: "Approve brief" })).toBeVisible();
});

test("phone: tabs scroll and the approve bar is visible without scrolling", async ({ page }) => {
  await page.setViewportSize({ width: 375, height: 812 });
  await startRun(page);
  await waitForGate1(page);
  await expect(page.locator(".steplog[open]")).toHaveCount(0);

  const tabs = page.getByRole("navigation", { name: "Run pages" });
  const fits = await tabs.evaluate((el) => ({ scroll: el.scrollWidth, client: el.clientWidth, overflow: getComputedStyle(el).overflowX }));
  expect(fits.overflow).toBe("auto");
  expect(fits.client).toBeLessThanOrEqual(375);

  await page.getByRole("link", { name: "Brief", exact: true }).click();
  await expect(page.getByTestId("brief-version")).toBeVisible();
  const approve = page.getByRole("button", { name: "Approve brief" });
  await expect(approve).toBeInViewport();
  const bar = await page.getByRole("region", { name: "Gate 1 decision" }).boundingBox();
  const tabbar = await page.getByRole("navigation", { name: "Main tabs" }).boundingBox();
  expect(bar && tabbar && bar.y + bar.height <= tabbar.y).toBeTruthy(); // the bar sits above the tab bar
  expect(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth)).toBe(true);
});
