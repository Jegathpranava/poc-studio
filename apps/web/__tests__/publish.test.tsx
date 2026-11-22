import { cleanup, fireEvent, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DeliveredView } from "@/components/publish/delivered-view";
import { Gate2View } from "@/components/publish/gate2-view";
import { QaReportPanel } from "@/components/publish/qa-report";
import type { PublishStatus, QaReport, RunDetail } from "@/lib/api";
import { canPublish, defaultRepoName, qaView, runTimes, validateRepoName } from "@/lib/publish";

vi.mock("@/components/shell/notify", () => ({ notify: { success: vi.fn(), error: vi.fn(), info: vi.fn() } }));

const check = (name: string, ok = true, detail = "ok") => ({ name, ok, detail, owner_agent: "port", report_only: false });
const report = (over: Partial<QaReport> = {}): QaReport => ({
  checks: [check("deck_present"), check("build_passed"), check("no_secrets")],
  passed: ["deck_present", "build_passed", "no_secrets"],
  failed: [],
  send_back: null,
  block_publish: false,
  sent_back_count: 0,
  ...over,
});

const detail = {
  id: "r_aaaaaa",
  title: "Dock scheduling PoC",
  client_name: "Acme Freight",
  status: "waiting_gate2",
  paid_usd: 0.012,
  budget_usd: 0.05,
  started_at: "2026-11-22T10:00:00Z",
  steps: [
    { agent: "intelligence", started_at: "2026-11-22T10:00:00Z", finished_at: "2026-11-22T10:00:30Z" },
    { agent: "gate1", started_at: "2026-11-22T10:02:30Z", finished_at: "2026-11-22T10:02:30Z" },
    { agent: "qa", started_at: "2026-11-22T10:05:00Z", finished_at: "2026-11-22T10:05:20Z" },
  ],
  artifacts: [{ type: "video", path: "r_aaaaaa/deck/x.mp4" }],
} as unknown as RunDetail;

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

function stubApi(qa: QaReport, refuse?: string) {
  const posts: unknown[] = [];
  vi.stubGlobal(
    "fetch",
    vi.fn((url: string, init?: RequestInit) => {
      if (init?.method === "POST") {
        posts.push(JSON.parse(String(init.body)));
        if (refuse) return Promise.resolve(json({ detail: refuse }, 409));
        return Promise.resolve(json({ run_id: "r_aaaaaa", gate: "publish", decision: "approve", status: "running" }));
      }
      if (url.endsWith("/artifacts/qa_report")) return Promise.resolve(json({ type: "qa_report", version: 1, data: qa }));
      if (url.endsWith("/artifacts/requirements")) {
        return Promise.resolve(json({ type: "requirements", version: 1, data: { action_items: [{}, {}, {}] } }));
      }
      if (url.endsWith("/files")) return Promise.resolve(json([{ name: "package.json", path: "package.json", type: "file" }]));
      if (url.endsWith("/api/health")) return Promise.resolve(json({ status: "ok", github_mode: "mock" }));
      return Promise.resolve(json({ detail: "no" }, 404));
    }),
  );
  return posts;
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("repo name validation", () => {
  it("accepts GitHub-safe names and rejects the rest", () => {
    expect(validateRepoName("acme-dock_poc.v2")).toBeNull();
    for (const bad of ["", "has space", "a/b", "x".repeat(101), "..", "repo.git"]) {
      expect(validateRepoName(bad)).not.toBeNull();
    }
  });

  it("builds the default name like the API does", () => {
    expect(defaultRepoName("Acme Freight", "Acme Freight PoC")).toBe("acme-freight-poc");
    expect(defaultRepoName("Acme", "Dock scheduling")).toBe("acme-dock-scheduling-poc");
  });

  it("only allows publishing with a clean name and no QA block", () => {
    expect(canPublish(report(), null, false)).toBe(true);
    expect(canPublish(report({ block_publish: true }), null, false)).toBe(false);
    expect(canPublish(report(), "bad", false)).toBe(false);
    expect(canPublish(null, null, false)).toBe(false);
  });
});

describe("QA report", () => {
  it("lists every check with its mark, and the build and deck notes", () => {
    const r = report({
      checks: [check("deck_present", false, "no deck HTML artifact was produced"), check("build_passed", false, "next build failed"), check("no_secrets")],
      sent_back_count: 1,
    });
    render(<QaReportPanel report={r} />);
    expect(screen.getByText("1 of 3 checks passed")).toBeTruthy();
    expect(screen.getAllByLabelText("Failed")).toHaveLength(2);
    expect(screen.getAllByLabelText("Passed")).toHaveLength(1);
    expect(screen.getByText("Repo code did not build.")).toBeTruthy();
    expect(screen.getByText("The deck is missing.")).toBeTruthy();
    expect(screen.getByText("no deck HTML artifact was produced")).toBeTruthy();
    expect(screen.getByTestId("sent-back").textContent).toMatch(/Sent back once/);
    expect(qaView(r).buildFailed).toBe(true);
  });
});

describe("Gate 2", () => {
  it("mounts the share actions in the header", async () => {
    stubApi(report());
    render(<Gate2View runId="r_aaaaaa" detail={detail} onSubmitted={() => undefined} />);
    expect(screen.getByRole("button", { name: /Copy client share link/ })).toBeTruthy();
    expect(screen.getByRole("button", { name: /Download share zip/ })).toBeTruthy();
    await screen.findByRole("button", { name: "Publish to GitHub" });
  });

  it("disables Publish and shows the blocked banner when QA says block_publish", async () => {
    stubApi(report({ block_publish: true, checks: [check("no_secrets", false, "app/leak.ts:1 github_token")] }));
    render(<Gate2View runId="r_aaaaaa" detail={detail} onSubmitted={() => undefined} />);
    expect(await screen.findByTestId("blocked-banner")).toBeTruthy();
    const publish = screen.getByRole("button", { name: "Publish to GitHub" }) as HTMLButtonElement;
    expect(publish.disabled).toBe(true);
  });

  it("disables Publish while the repo name is invalid, with a message", async () => {
    stubApi(report());
    render(<Gate2View runId="r_aaaaaa" detail={detail} onSubmitted={() => undefined} />);
    const publish = (await screen.findByRole("button", { name: "Publish to GitHub" })) as HTMLButtonElement;
    await waitFor(() => expect(publish.disabled).toBe(false));
    fireEvent.change(screen.getByLabelText("Name"), { target: { value: "bad name" } });
    expect(publish.disabled).toBe(true);
    expect(screen.getByText("Use letters, numbers, dots, dashes and underscores only.")).toBeTruthy();
  });

  it("confirms with the exact repo path, then posts the options", async () => {
    const posts = stubApi(report());
    const onSubmitted = vi.fn();
    render(<Gate2View runId="r_aaaaaa" detail={detail} onSubmitted={onSubmitted} />);
    expect(await screen.findByTestId("mock-note")).toBeTruthy();
    fireEvent.change(screen.getByLabelText("Name"), { target: { value: "acme-dock-poc" } });
    fireEvent.click(screen.getByRole("switch", { name: "Add GitHub Actions CI" }));
    fireEvent.click(screen.getByRole("button", { name: "Publish to GitHub" }));
    const summary = screen.getByTestId("confirm-summary").textContent ?? "";
    expect(summary).toContain("Jegathpranava/acme-dock-poc");
    expect(summary).toContain("private");
    expect(summary).toContain("opens 3 issues");
    expect(within(screen.getByRole("dialog")).getByText(/Nothing has left your machine yet/)).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Publish" }));
    await waitFor(() => expect(onSubmitted).toHaveBeenCalled());
    expect(posts).toEqual([
      { decision: "approve", options: { repo_name: "acme-dock-poc", private: true, open_issues: true, add_ci: false } },
    ]);
  });

  it("shows an API refusal inside the modal and stays open", async () => {
    stubApi(report(), "QA blocked the publish: a secret was found in the generated files. Fix it and run QA again.");
    const onSubmitted = vi.fn();
    render(<Gate2View runId="r_aaaaaa" detail={detail} onSubmitted={onSubmitted} />);
    const publish = (await screen.findByRole("button", { name: "Publish to GitHub" })) as HTMLButtonElement;
    await waitFor(() => expect(publish.disabled).toBe(false));
    fireEvent.click(publish);
    fireEvent.click(screen.getByRole("button", { name: "Publish" }));
    expect(await screen.findByText(/QA blocked the publish/)).toBeTruthy();
    expect(onSubmitted).not.toHaveBeenCalled();
    expect(screen.getByRole("dialog")).toBeTruthy();
  });
})

describe("Delivered", () => {
  const status = {
    status: "delivered",
    mode: "mock",
    blocked: false,
    result: {
      repo_url: "https://github.com/Jegathpranava/acme-dock-poc",
      name: "acme-dock-poc",
      private: true,
      issues: ["https://github.com/Jegathpranava/acme-dock-poc/issues/1"],
      pushed: false,
      mode: "mock",
      file_count: 41,
    },
  } as unknown as PublishStatus;

  it("renders the deliverable links", () => {
    const done = { ...detail, status: "delivered" } as RunDetail;
    render(<DeliveredView runId="r_aaaaaa" detail={done} status={status} />);
    expect(screen.getByRole("heading", { name: "Delivered in 3m 20s" })).toBeTruthy();
    const repo = screen.getByRole("link", { name: /GitHub repo/ });
    expect(repo.getAttribute("href")).toBe("https://github.com/Jegathpranava/acme-dock-poc");
    expect(repo.getAttribute("target")).toBe("_blank");
    expect(screen.getByRole("link", { name: /Prototype/ }).getAttribute("href")).toBe("/runs/r_aaaaaa/prototype");
    expect(screen.getByRole("link", { name: /Pitch deck/ }).getAttribute("href")).toBe("/runs/r_aaaaaa/deck");
    expect(screen.getByRole("link", { name: /Walkthrough video/ }).getAttribute("href")).toBe("/runs/r_aaaaaa/deck");
    expect(screen.getByRole("link", { name: /Architecture spec/ }).getAttribute("href")).toBe("/runs/r_aaaaaa/architecture");
    expect(screen.queryByText("Coming soon")).toBeNull();
    expect(screen.getByRole("link", { name: /Client share page/ }).getAttribute("href")).toBe("#share-actions");
    expect((screen.getByRole("button", { name: /Copy client share link/ }) as HTMLButtonElement).disabled).toBe(false);
    expect(screen.getByRole("button", { name: /Download share zip/ })).toBeTruthy();
    expect(screen.getByText(/Nothing was sent to GitHub/)).toBeTruthy();
  });
});

describe("run times", () => {
  it("subtracts the Gate 1 wait from agent time", () => {
    const t = runTimes(detail);
    expect(t.agentMs).toBe(5 * 60_000 + 20_000 - 2 * 60_000); // run start to QA done, minus the 2 min wait at Gate 1
    expect(t.gateMs).toBe(2 * 60_000);
  });
});
