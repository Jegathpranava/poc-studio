import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DeckPanel } from "@/components/deck/deck-panel";
import { DeckView } from "@/components/deck/deck-view";
import { VideoPanel } from "@/components/deck/video-panel";

const run = vi.hoisted(() => ({
  value: {
    runId: "r_aaaaaa",
    status: "waiting_gate2",
    detailError: null,
    detail: { steps: [], artifacts: [{ type: "deck", path: "r_aaaaaa/deck/x.v1.html" }] },
  } as Record<string, unknown>,
}));
vi.mock("@/components/run/run-context", () => ({ useRun: () => run.value }));

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

describe("Deck and video page", () => {
  it("clicking a chapter seeks the video", () => {
    render(
      <VideoPanel
        runId="r_aaaaaa"
        video={{ state: "ready", chapters: [{ t: 0, title: "Welcome" }, { t: 42.5, title: "Dashboard" }] }}
      />,
    );
    const video = document.querySelector("video") as HTMLVideoElement;
    video.play = vi.fn(() => Promise.resolve());
    fireEvent.click(screen.getByRole("button", { name: /Dashboard/ }));
    expect(video.currentTime).toBe(42.5);
    expect(video.getAttribute("src")).toMatch(/\/api\/runs\/r_aaaaaa\/video$/);
    expect(screen.getByRole("link", { name: /Download MP4/ })).toBeTruthy();
  });

  it("the deck iframe is sandboxed without same-origin and the full-screen link opens a new tab", () => {
    render(<DeckPanel runId="r_aaaaaa" />);
    const frame = screen.getByTitle("Interactive deck preview");
    expect(frame.getAttribute("sandbox")).toBe("allow-scripts");
    expect(frame.getAttribute("src")).toMatch(/\/api\/runs\/r_aaaaaa\/deck\.html$/);
    expect(screen.getByRole("link", { name: /Open full screen/ }).getAttribute("target")).toBe("_blank");
  });

  it("shows the missing state when the chapters return 404", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.resolve(json({ detail: "no video" }, 404))));
    render(<DeckView />);
    expect(await screen.findByText("The video is recorded after you approve Gate 2.")).toBeTruthy();
    expect(document.querySelector("video")).toBeNull();
  });

  it("shows the recorder error when the video step failed", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.resolve(json({ detail: "no video" }, 404))));
    run.value = {
      ...run.value,
      detail: {
        steps: [{ agent: "video", status: "failed", error_message: "Chromium crashed" }],
        artifacts: [{ type: "deck", path: "x.html" }],
      },
    };
    render(<DeckView />);
    expect(await screen.findByText("Chromium crashed")).toBeTruthy();
  });
});
