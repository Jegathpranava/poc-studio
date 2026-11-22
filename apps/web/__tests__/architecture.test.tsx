import { cleanup, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { ArchitectureView } from "@/components/architecture/architecture-view";
import { CostTable } from "@/components/architecture/cost-table";
import { MermaidDiagram } from "@/components/architecture/mermaid-diagram";
import type { Architecture } from "@/lib/architecture";

const renderMock = vi.fn(async (id: string, source: string) => ({ svg: `<svg data-id="${id}" data-n="${source.length}"></svg>` }));
vi.mock("mermaid", () => ({
  default: { initialize: vi.fn(), render: (id: string, src: string) => renderMock(id, src) },
}));
vi.mock("@/components/run/run-context", () => ({ useRun: () => ({ runId: "r_aaaaaa", status: "waiting_gate2" }) }));

const ARCH: Architecture = {
  use_case_class: "other",
  components: [],
  mermaid: "flowchart LR\n  A --> B",
  models: [{ job: "Summaries", model: "fast", cost_per_1k_calls_usd: 0 }],
  monthly_cost: {
    lines: [
      { item: "Hosting", usd: 25 },
      { item: "Database", usd: 20 },
    ],
    total_usd: 45,
    assumptions: "Small.",
  },
  phases: [{ name: "Build", weeks: 2, detail: "Do it." }],
  rationale: "Because.",
};

const reply = (body: unknown, status: number) => vi.fn(() => Promise.resolve(new Response(JSON.stringify(body), { status })));

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  renderMock.mockClear();
});

describe("Architecture page", () => {
  it("the cost table renders the total", () => {
    render(<CostTable cost={ARCH.monthly_cost} />);
    expect(screen.getByText("Total").closest("tr")?.textContent).toContain("$45.00");
  });

  it("passes the mermaid source to the renderer", async () => {
    render(<MermaidDiagram source={ARCH.mermaid} label="Diagram" />);
    await waitFor(() => expect(screen.getByTestId("diagram")).toBeTruthy());
    expect(renderMock).toHaveBeenCalledWith(expect.any(String), ARCH.mermaid);
  });

  it("shows the empty state when the API returns 404", async () => {
    vi.stubGlobal("fetch", reply({ detail: "none" }, 404));
    render(<ArchitectureView />);
    expect(await screen.findByText("Available after the Solution Architect runs")).toBeTruthy();
  });

  it("shows the diagram, tables and download link when loaded", async () => {
    vi.stubGlobal("fetch", reply({ type: "architecture", version: 1, data: ARCH }, 200));
    render(<ArchitectureView />);
    expect(await screen.findByTestId("diagram")).toBeTruthy();
    const link = screen.getByRole("link", { name: /download \.md/i });
    expect(link.getAttribute("href")).toContain("/artifacts/architecture/markdown");
    expect(screen.getByText("Total")).toBeTruthy();
  });
});
