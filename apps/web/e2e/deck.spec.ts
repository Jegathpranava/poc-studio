import path from "node:path";

import { expect, test } from "@playwright/test";

const SAMPLE = path.resolve(__dirname, "../../../services/api/tests/ingest/fixtures/sample.vtt");
const API = "http://127.0.0.1:8000";

// The Prototype Builder runs a real `npm ci` and `next build`; the recorder is the API's VIDEO_FAKE clip.
test.setTimeout(6 * 60_000);

test("approve both gates, then see the deck in its frame and the video with chapters", async ({ page, request }) => {
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

  // The Gate 2 screen is a later task: approve through the API.
  const res = await request.post(`${API}/api/runs/${runId}/gates/publish`, { data: { decision: "approve" } });
  expect(res.ok()).toBeTruthy();
  await expect
    .poll(async () => (await request.get(`${API}/api/runs/${runId}/video/chapters`)).status(), { timeout: 60_000 })
    .toBe(200);

  await page.goto(`/runs/${runId}/deck`);
  const iframe = page.locator("iframe[title='Interactive deck preview']");
  await expect(iframe).toHaveAttribute("src", new RegExp(`/api/runs/${runId}/deck\\.html$`));
  await expect(iframe).toHaveAttribute("sandbox", "allow-scripts");
  const deck = await request.get(`${API}/api/runs/${runId}/deck.html`);
  expect(deck.status()).toBe(200);
  await expect(page.getByRole("link", { name: /Open full screen/ })).toHaveAttribute("target", "_blank");

  const video = page.locator("video");
  await expect(video).toBeVisible();
  await expect.poll(() => video.evaluate((v: HTMLVideoElement) => v.readyState)).toBeGreaterThanOrEqual(1);
  expect(await page.locator(".chapters li").count()).toBeGreaterThanOrEqual(1);
  await expect(page.getByRole("link", { name: /Download MP4/ })).toBeVisible();
});
