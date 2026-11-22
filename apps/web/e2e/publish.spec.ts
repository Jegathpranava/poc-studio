import path from "node:path";

import { expect, test } from "@playwright/test";

const SAMPLE = path.resolve(__dirname, "../../../services/api/tests/ingest/fixtures/sample.vtt");

// The Prototype Builder runs a real `npm ci` and `next build`; the recorder is the API's VIDEO_FAKE clip and
// GitHub is mocked (GITHUB_MODE=mock), so nothing is sent anywhere.
test.setTimeout(6 * 60_000);

test("Gate 2 lists the QA checks, publishes in mock mode and shows Delivered", async ({ page }) => {
  await page.goto("/runs/new");
  await page.getByTestId("file-input").setInputFiles(SAMPLE);
  await page.getByLabel("Client name").fill("Acme Freight");
  await page.getByRole("button", { name: "Start run" }).click();
  await expect(page).toHaveURL(/\/runs\/r_[0-9a-f]{6}$/);
  const runId = page.url().split("/").pop() ?? "";
  await expect(page.locator('.gate[data-gate="gate1"]')).toHaveAttribute("data-view", "waiting");

  await page.getByRole("link", { name: "Brief", exact: true }).click();
  await page.getByRole("region", { name: "Gate 1 decision" }).getByRole("button", { name: "Approve brief" }).click();
  await expect(page.getByText("Brief approved", { exact: true })).toBeVisible();
  await expect(page.locator('.gate[data-gate="gate2"]')).toHaveAttribute("data-view", "waiting", { timeout: 4 * 60_000 });

  await page.goto(`/runs/${runId}/publish`);
  await expect(page.getByRole("heading", { name: "Ready to publish" })).toBeVisible();
  await expect(page.getByTestId("mock-note")).toContainText("Mock mode: nothing is sent to GitHub");
  const checks = page.getByRole("list", { name: "QA checks" }).getByRole("listitem");
  await expect(checks.first()).toBeVisible();
  expect(await checks.count()).toBeGreaterThanOrEqual(5);
  await expect(page.getByTestId("blocked-banner")).toHaveCount(0);

  // Phone width: the sticky Gate 2 bar stays on screen, above the tab bar.
  await page.setViewportSize({ width: 375, height: 812 });
  const bar = page.getByRole("region", { name: "Gate 2 decision" });
  await expect(bar).toBeInViewport();
  await expect(bar.getByRole("button", { name: "Publish to GitHub" })).toBeInViewport();
  await page.setViewportSize({ width: 1280, height: 800 });

  await page.getByLabel("Name", { exact: true }).fill("e2e-acme-poc");
  await bar.getByRole("button", { name: "Publish to GitHub" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByTestId("confirm-summary")).toContainText("Jegathpranava/e2e-acme-poc");
  await expect(dialog).toContainText("Nothing has left your machine yet.");
  await dialog.getByRole("button", { name: "Publish", exact: true }).click();

  await expect(page.getByRole("heading", { name: /^Delivered in / })).toBeVisible({ timeout: 60_000 });
  const repo = page.getByRole("link", { name: /GitHub repo/ });
  await expect(repo).toHaveAttribute("href", "https://github.com/Jegathpranava/e2e-acme-poc");
  await expect(repo).toHaveAttribute("target", "_blank");
  await expect(page.getByRole("link", { name: /Client share page/ })).toBeVisible();
  await expect(page.getByRole("link", { name: /Pitch deck/ })).toHaveAttribute("href", `/runs/${runId}/deck`);
});
