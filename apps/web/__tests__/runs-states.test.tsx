import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { RunsView } from "@/components/runs/runs-view";
import type { RunSummary } from "@/lib/api";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ push: vi.fn() }),
  usePathname: () => "/",
}));

function run(over: Partial<RunSummary>): RunSummary {
  return {
    id: "r_aaaaaa",
    title: "Dispatch copilot",
    client_name: "Kestrel Freight Co.",
    sector: "Logistics",
    status: "running",
    current_step: null,
    paid_usd: 0,
    budget_usd: 0.05,
    started_at: new Date().toISOString(),
    finished_at: null,
    ...over,
  };
}

function mockFetch(impl: () => Promise<Response>) {
  vi.stubGlobal("fetch", vi.fn(impl));
}

const json = (body: unknown) => Promise.resolve(new Response(JSON.stringify(body), { status: 200 }));

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("Runs page states", () => {
  it("shows the empty state when the API returns no runs", async () => {
    mockFetch(() => json([]));
    render(<RunsView />);
    expect(await screen.findByText("Start your first run")).toBeTruthy();
  });

  it("shows the error state naming port 8000 when the fetch rejects", async () => {
    mockFetch(() => Promise.reject(new TypeError("Failed to fetch")));
    render(<RunsView />);
    expect(await screen.findByText(/port 8000/)).toBeTruthy();
    expect(screen.getByRole("button", { name: /try again/i })).toBeTruthy();
  });

  it("shows a busy skeleton while the fetch is pending", () => {
    mockFetch(() => new Promise<Response>(() => {}));
    render(<RunsView />);
    expect(screen.getByLabelText("Loading runs").getAttribute("aria-busy")).toBe("true");
  });

  it("renders both client names for two rows", async () => {
    mockFetch(() =>
      json([
        run({ id: "r_aaaaaa", client_name: "Kestrel Freight Co." }),
        run({ id: "r_bbbbbb", client_name: "Vela Pay", status: "delivered", sector: "Fintech" }),
      ]),
    );
    render(<RunsView />);
    expect(await screen.findByText("Kestrel Freight Co.")).toBeTruthy();
    expect(screen.getByText("Vela Pay")).toBeTruthy();
  });
});
