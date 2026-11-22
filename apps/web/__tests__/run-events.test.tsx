import { act, cleanup, render, renderHook, screen } from "@testing-library/react";
import type { ReactNode } from "react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { RunFrame } from "@/components/run/run-frame";
import { useRun } from "@/components/run/run-context";
import { MAX_FIRST_FAILURES, eventsUrl, useRunEvents } from "@/components/run/use-run-events";

const nav = vi.hoisted(() => ({ id: "r_aaaaaa" }));
vi.mock("next/navigation", () => ({
  useParams: () => ({ id: nav.id }),
  usePathname: () => `/runs/${nav.id}`,
  useRouter: () => ({ push: vi.fn() }),
}));

class FakeEventSource {
  static instances: FakeEventSource[] = [];
  static CONNECTING = 0;
  static OPEN = 1;
  static CLOSED = 2;
  readyState = 0;
  onopen: (() => void) | null = null;
  onerror: (() => void) | null = null;
  listeners: Record<string, ((m: MessageEvent<string>) => void)[]> = {};
  constructor(readonly url: string) {
    FakeEventSource.instances.push(this);
  }
  addEventListener(type: string, fn: (m: MessageEvent<string>) => void) {
    (this.listeners[type] ??= []).push(fn);
  }
  close() {
    this.readyState = 2;
  }
  fail() {
    this.readyState = 2;
    this.onerror?.();
  }
  emit(id: number, agent = "intelligence") {
    const data = JSON.stringify({ id, ts: "2026-11-22T10:00:00Z", run_id: nav.id, agent, kind: "status", status: "running" });
    this.listeners["step"]?.forEach((fn) => fn({ data } as MessageEvent<string>));
  }
}

beforeEach(() => {
  FakeEventSource.instances = [];
  nav.id = "r_aaaaaa";
  vi.useFakeTimers();
  vi.stubGlobal("EventSource", FakeEventSource);
  vi.stubGlobal("fetch", vi.fn(() => new Promise<Response>(() => {})));
});

afterEach(() => {
  cleanup();
  vi.useRealTimers();
  vi.unstubAllGlobals();
});

const latest = () => FakeEventSource.instances[FakeEventSource.instances.length - 1];

describe("useRunEvents stop condition", () => {
  it("gives up after 3 failed connects when no event ever arrived", () => {
    const { result } = renderHook(() => useRunEvents("r_x"));
    for (let i = 0; i < MAX_FIRST_FAILURES; i++) {
      act(() => latest().fail());
      act(() => void vi.advanceTimersByTime(20000));
    }
    expect(result.current.connection).toBe("failed");
    expect(FakeEventSource.instances).toHaveLength(MAX_FIRST_FAILURES);
    act(() => void vi.advanceTimersByTime(60000));
    expect(FakeEventSource.instances).toHaveLength(MAX_FIRST_FAILURES); // nothing reconnects by itself
  });

  it("retry connects again", () => {
    const { result } = renderHook(() => useRunEvents("r_x"));
    for (let i = 0; i < MAX_FIRST_FAILURES; i++) {
      act(() => latest().fail());
      act(() => void vi.advanceTimersByTime(20000));
    }
    act(() => result.current.retry());
    expect(FakeEventSource.instances).toHaveLength(MAX_FIRST_FAILURES + 1);
    expect(result.current.connection).toBe("connecting");
  });

  it("keeps reconnecting, with the last id, once events have arrived", () => {
    const { result } = renderHook(() => useRunEvents("r_x"));
    act(() => latest().emit(5));
    for (let i = 0; i < 5; i++) {
      act(() => latest().fail());
      act(() => void vi.advanceTimersByTime(20000));
    }
    expect(result.current.connection).toBe("reconnecting");
    expect(FakeEventSource.instances).toHaveLength(6);
    expect(FakeEventSource.instances[0].url).not.toContain("after=");
    expect(latest().url).toContain("/api/runs/r_x/events?after=5");
  });

  it("does not connect when the run is known to be missing", () => {
    renderHook(() => useRunEvents("r_x", { halt: true }));
    expect(FakeEventSource.instances).toHaveLength(0);
  });

  it("adds ?after only when there is a last id", () => {
    expect(eventsUrl("r_x", 0)).toMatch(/events$/);
    expect(eventsUrl("r_x", 9)).toMatch(/events\?after=9$/);
  });
});

function Probe(): ReactNode {
  const { runId, timeline } = useRun();
  return (
    <p data-testid="probe">
      {runId}|{timeline.lastId}|{Object.keys(timeline.rows).join(",")}
    </p>
  );
}

describe("RunFrame", () => {
  it("shows no rows of run A after switching to run B", () => {
    const { rerender } = render(
      <RunFrame>
        <Probe />
      </RunFrame>,
    );
    act(() => latest().emit(7));
    expect(screen.getByTestId("probe").textContent).toBe("r_aaaaaa|7|intelligence");

    nav.id = "r_bbbbbb";
    rerender(
      <RunFrame>
        <Probe />
      </RunFrame>,
    );
    expect(screen.getByTestId("probe").textContent).toBe("r_bbbbbb|0|");
    expect(latest().url).toContain("r_bbbbbb");
  });
});
