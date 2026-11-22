import path from "node:path";

import { expect, test } from "@playwright/test";

const SAMPLE = path.resolve(__dirname, "../../../services/api/tests/ingest/fixtures/sample.vtt");
const API = "http://127.0.0.1:8000";

// The Prototype Builder runs a real `npm ci` and `next build`; the LLM is the mock provider.
test.setTimeout(8 * 60_000);

test("request changes on the deck at Gate 2 reruns only Pitch and Docs, then returns to Gate 2", async ({ page, request }) => {
  await page.goto("/runs/new");
  await page.getByTestId("file-input").setInputFiles(SAMPLE);
  await page.getByLabel("Client name").fill("Kestrel Freight Co.");
  await page.getByRole("button", { name: "Start run" }).click();
  await expect(page).toHaveURL(/\/runs\/r_[0-9a-f]{6}$/);
  const runId = page.url().split("/").pop() ?? "";
  await expect(page.locator('.gate[data-gate="gate1"]')).toHaveAttribute("data-view", "waiting");

  await page.getByRole("link", { name: "Brief", exact: true }).click();
  await page.getByRole("region", { name: "Gate 1 decision" }).getByRole("button", { name: "Approve brief" }).click();
  await expect(page.getByText("Brief approved", { exact: true })).toBeVisible();
  await expect(page.locator(".badge", { hasText: "Waiting at Gate 2" })).toBeVisible({ timeout: 5 * 60_000 });

  await page.getByRole("link", { name: "Deck and video" }).click();
  await expect(page.locator("iframe[title='Interactive deck preview']")).toBeVisible();
  await page.getByRole("button", { name: "Request changes" }).click();
  const dialog = page.getByRole("dialog");
  await dialog.getByLabel("Note").fill("Lead with the cost saving.");
  await dialog.getByRole("button", { name: "Send" }).click();

  await expect(page.getByText("Change request sent", { exact: true })).toBeVisible();
  await expect(page).toHaveURL(new RegExp(`/runs/${runId}$`));

  // Back at Gate 2 with a second pitch run; nothing upstream ran again.
  const pitch = page.locator('.step[data-agent="pitch"]');
  await expect(pitch.locator(".tag.attempt")).toContainText("Attempt 2", { timeout: 2 * 60_000 });
  await expect(page.locator(".badge", { hasText: "Waiting at Gate 2" })).toBeVisible({ timeout: 2 * 60_000 });
  await expect(page.locator('.step[data-agent="intelligence"] .tag.attempt')).toHaveCount(0);
  await expect(page.locator('.step[data-agent="screens"] .tag.attempt')).toHaveCount(0);

  const detail = (await (await request.get(`${API}/api/runs/${runId}`)).json()) as {
    steps: { agent: string }[];
    artifacts: { type: string; path: string }[];
  };
  const count = (agent: string) => detail.steps.filter((s) => s.agent === agent).length;
  expect([count("pitch"), count("architect"), count("screens"), count("port")]).toEqual([2, 1, 1, 1]);
  expect(detail.artifacts.filter((a) => a.type === "deck" && a.path.endsWith(".json"))).toHaveLength(2);

  await page.getByRole("link", { name: "Deck and video" }).click();
  await expect(page.getByRole("button", { name: "Request changes" })).toBeEnabled();
});
