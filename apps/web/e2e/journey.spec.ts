import path from "node:path";

import { expect, test } from "@playwright/test";

const SAMPLE = path.resolve(__dirname, "../../../services/api/tests/ingest/fixtures/sample.vtt");

// The whole product path on mocks: the API uses the mock LLM, VIDEO_FAKE=1 and the mock GitHub. The port runs
// a real `npm ci` and `next build`, so the run takes a few minutes.
test.setTimeout(6 * 60_000);

test("journey: new run, brief, Gate 2 review of every page, publish, Delivered, back on the Runs list", async ({ page }) => {
  // Runs (empty or not): the page loads and offers a way to start.
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Runs", level: 1 })).toBeVisible();

  // New run: upload the sample, pick a sector in the combobox.
  await page.goto("/runs/new");
  await page.getByTestId("file-input").setInputFiles(SAMPLE);
  await expect(page.getByText("sample.vtt")).toBeVisible();
  await page.getByLabel("Client name").fill("Acme Freight");
  await page.getByRole("button", { name: "Sector" }).click();
  await page.getByRole("option", { name: "Logistics" }).click();
  await page.getByRole("button", { name: "Start run" }).click();
  await expect(page).toHaveURL(/\/runs\/r_[0-9a-f]{6}$/);
  const runId = page.url().split("/").pop() ?? "";

  // Timeline, then the Brief: edit the budget and approve.
  await expect(page.locator('.gate[data-gate="gate1"]')).toHaveAttribute("data-view", "waiting");
  await expect(page.locator('.step[data-agent="intelligence"]')).toHaveAttribute("data-state", "done");
  await page.getByRole("link", { name: "Brief", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Review the brief" })).toBeVisible();
  await page.getByLabel("Budget", { exact: true }).fill("About $88k");
  await page.getByRole("region", { name: "Gate 1 decision" }).getByRole("button", { name: "Approve brief" }).click();
  await expect(page.getByText("Brief approved", { exact: true })).toBeVisible();
  await expect(page).toHaveURL(/\/runs\/r_[0-9a-f]{6}$/);

  // Gate 2 is reached once the architect, screens, pitch, port, assemble and QA steps are done.
  await expect(page.locator('.gate[data-gate="gate2"]')).toHaveAttribute("data-view", "waiting", { timeout: 4 * 60_000 });

  // Phone width on the Timeline: tabs scroll, logs stay collapsed, the page does not scroll sideways.
  await page.setViewportSize({ width: 375, height: 812 });
  await page.goto(`/runs/${runId}`);
  await expect(page.locator('.gate[data-gate="gate2"]')).toHaveAttribute("data-view", "waiting");
  await expect(page.locator(".steplog[open]")).toHaveCount(0);
  const tabs = page.getByRole("navigation", { name: "Run pages" });
  const overflowX = await tabs.evaluate((el) => getComputedStyle(el).overflowX);
  expect(["auto", "scroll"]).toContain(overflowX);
  const pageOverflow = await page.evaluate(() => document.documentElement.scrollWidth - document.documentElement.clientWidth);
  expect(pageOverflow).toBeLessThanOrEqual(0);
  await page.setViewportSize({ width: 1280, height: 800 });

  // Architecture: the diagram renders.
  await page.getByRole("link", { name: "Architecture", exact: true }).click();
  await expect(page.getByTestId("diagram").locator("svg")).toBeVisible();

  // Prototype: the live preview shows the client name.
  await page.getByRole("link", { name: "Prototype", exact: true }).click();
  const proto = page.locator("iframe[title='Prototype preview']");
  await expect(proto).toHaveAttribute("src", /^http:\/\/127\.0\.0\.1:43\d\d\/$/, { timeout: 90_000 });
  await expect(page.frameLocator("iframe[title='Prototype preview']").locator("body")).toContainText("Acme", {
    timeout: 60_000,
  });

  // Publish: QA checks are listed; the bar fits a phone; confirm Publish. The video is recorded after
  // approval, so the Deck page is checked after it.
  await page.getByRole("link", { name: "Publish", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Ready to publish" })).toBeVisible();
  const checks = page.getByRole("list", { name: "QA checks" }).getByRole("listitem");
  await expect(checks.first()).toBeVisible();
  expect(await checks.count()).toBeGreaterThanOrEqual(5);
  await page.setViewportSize({ width: 375, height: 812 });
  const bar = page.getByRole("region", { name: "Gate 2 decision" });
  await expect(bar).toBeInViewport();
  await expect(bar.getByRole("button", { name: "Publish to GitHub" })).toBeInViewport();
  await page.setViewportSize({ width: 1280, height: 800 });

  await page.getByLabel("Name", { exact: true }).fill("e2e-journey-poc");
  await bar.getByRole("button", { name: "Publish to GitHub" }).click();
  const dialog = page.getByRole("dialog");
  await expect(dialog.getByTestId("confirm-summary")).toContainText("e2e-journey-poc");
  await dialog.getByRole("button", { name: "Publish", exact: true }).click();

  // Delivered: the mock repo URL.
  await expect(page.getByRole("heading", { name: /^Delivered in / })).toBeVisible({ timeout: 90_000 });
  await expect(page.getByRole("link", { name: /GitHub repo/ })).toHaveAttribute(
    "href",
    "https://github.com/Jegathpranava/e2e-journey-poc",
  );

  // Deck and video: the deck frame loads and the video is ready.
  await page.getByRole("link", { name: "Deck and video", exact: true }).click();
  const deck = page.locator("iframe[title='Interactive deck preview']");
  await expect(deck).toHaveAttribute("src", new RegExp(`/api/runs/${runId}/deck\.html$`));
  await expect(deck.contentFrame().locator("body")).not.toBeEmpty();
  const video = page.locator("video");
  await expect(video).toBeVisible();
  await expect.poll(() => video.evaluate((v: HTMLVideoElement) => v.readyState)).toBeGreaterThanOrEqual(1);

  // Back to Runs: the run shows Delivered with its paid spend.
  await page.getByRole("link", { name: "Runs", exact: true }).first().click();
  await expect(page).toHaveURL(/\/$/);
  const row = page.locator("tr", { has: page.locator(`a[href="/runs/${runId}"]`) });
  await expect(row.getByText("Delivered")).toBeVisible();
  await expect(row).toContainText(/\$\d/);
});
