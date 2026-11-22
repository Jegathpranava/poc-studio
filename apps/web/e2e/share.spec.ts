import fs from "node:fs";
import path from "node:path";

import { expect, test, type APIRequestContext } from "@playwright/test";

const API = "http://127.0.0.1:8000";
const SAMPLE = path.resolve(__dirname, "../../../services/api/tests/ingest/fixtures/sample.vtt");

// Same journey as publish.spec.ts, driven through the API: a real `npm ci` and `next build`, the recorder is
// the VIDEO_FAKE clip and GitHub is mocked.
test.setTimeout(6 * 60_000);

async function status(request: APIRequestContext, id: string): Promise<string> {
  const res = await request.get(`${API}/api/runs/${id}`);
  return ((await res.json()) as { status: string }).status;
}

async function waitFor(request: APIRequestContext, id: string, wanted: string, ms: number) {
  await expect.poll(() => status(request, id), { timeout: ms, intervals: [1000] }).toBe(wanted);
}

test("a delivered run shares a zip and a token page without app chrome; settings shows no key", async ({
  page,
  request,
}) => {
  const created = await request.post(`${API}/api/runs`, {
    multipart: {
      files: { name: "sample.vtt", mimeType: "text/vtt", buffer: fs.readFileSync(SAMPLE) },
      client: "Acme Freight",
    },
  });
  expect(created.status()).toBe(201);
  const runId = ((await created.json()) as { id: string }).id;

  await waitFor(request, runId, "waiting_gate1", 60_000);
  const g1 = await request.post(`${API}/api/runs/${runId}/gates/scope`, { data: { decision: "approve" } });
  expect(g1.ok()).toBeTruthy();
  await waitFor(request, runId, "waiting_gate2", 4 * 60_000);

  // Gate 2 with a deck: sharing is allowed already.
  const early = await request.post(`${API}/api/share/${runId}`);
  expect(early.status()).toBe(200);

  const g2 = await request.post(`${API}/api/runs/${runId}/gates/publish`, {
    data: {
      decision: "approve",
      options: { repo_name: "e2e-share-poc", private: true, open_issues: true, add_ci: true },
    },
  });
  expect(g2.ok()).toBeTruthy();
  await waitFor(request, runId, "delivered", 60_000);

  const exported = await request.post(`${API}/api/runs/${runId}/share-export`);
  expect(exported.status()).toBe(200);
  const body = (await exported.json()) as { download_url: string; share_token: string };
  const zip = await request.get(`${API}${body.download_url}`);
  expect(zip.status()).toBe(200);
  expect((await zip.body()).subarray(0, 2).toString()).toBe("PK");

  const made = await request.post(`${API}/api/share/${runId}`);
  const token = ((await made.json()) as { token: string }).token;

  await page.goto(`/share/${token}`);
  await expect(page.locator("video")).toBeVisible();
  await expect(page.getByRole("link", { name: /Open the interactive deck/ })).toBeVisible();
  await expect(page.getByText("What we heard")).toBeVisible();
  await expect(page.getByText(/This page is read-only and expires on/)).toBeVisible();
  // No app chrome: the rail links are hidden and nothing on the page links into the app.
  await expect(page.getByRole("link", { name: "Settings" })).toHaveCount(0);
  await expect(page.locator(".rail")).toBeHidden();
  await expect(page.locator('.share-root a[href^="/"]')).toHaveCount(0);

  await page.goto("/share/not-a-real-token");
  await expect(page.getByText("This link has expired or is not valid")).toBeVisible();

  await page.goto("/settings");
  await expect(page.getByRole("heading", { name: "Settings" })).toBeVisible();
  await expect(page.getByTestId("key-OPENAI_API_KEY")).toContainText(/is (not )?set in \.env/);
  const text = await page.locator("main").innerText();
  expect(text).not.toMatch(/sk-[A-Za-z0-9]{8,}|ghp_[A-Za-z0-9]{8,}/);

  await page.goto("/templates");
  await expect(page.getByRole("table", { name: "Sector templates" })).toBeVisible();
  await expect(page.getByText("Logistics dispatch")).toBeVisible();
});
