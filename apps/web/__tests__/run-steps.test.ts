import { describe, expect, it } from "vitest";

import {
  costByModel,
  foldEvents,
  gateView,
  initialTimeline,
  reduceEvent,
  totals,
  type RunEvent,
} from "@/lib/run-steps";

let nextId = 0;
function ev(over: Partial<RunEvent> & Pick<RunEvent, "agent" | "kind">): RunEvent {
  nextId += 1;
  return { id: nextId, ts: new Date(Date.UTC(2026, 10, 22, 10, 0, nextId)).toISOString(), run_id: "r_aaaaaa", ...over };
}

const run = (status: string, kind: RunEvent["kind"] = "status") => ev({ agent: "run", kind, status });

describe("step-state reducer", () => {
  it("moves a step from idle to active to done", () => {
    nextId = 0;
    let s = initialTimeline();
    s = reduceEvent(s, ev({ agent: "intelligence", kind: "status", status: "running", attempt: 1, model: "fast" }));
    expect(s.rows.intelligence.state).toBe("active");
    expect(s.rows.intelligence.model).toBe("fast");
    s = reduceEvent(s, ev({ agent: "intelligence", kind: "status", status: "done", attempt: 1 }));
    expect(s.rows.intelligence.state).toBe("done");
    expect(s.rows.intelligence.finishedAt).not.toBeNull();
  });

  it("adds cost events to tokens, cost and model", () => {
    nextId = 0;
    const s = foldEvents([
      ev({ agent: "intelligence", kind: "status", status: "running", attempt: 1 }),
      ev({ agent: "intelligence", kind: "cost", model: "fast", tokens_in: 1000, tokens_out: 200, cost_usd: 0 }),
      ev({ agent: "intelligence", kind: "cost", model: "fast", tokens_in: 500, tokens_out: 100, cost_usd: 0.002 }),
    ]);
    expect(s.rows.intelligence).toMatchObject({ tokensIn: 1500, tokensOut: 300, costUsd: 0.002, model: "fast" });
    expect(totals(s)).toEqual({ tokens: 1800, costUsd: 0.002 });
    expect(costByModel(s)).toEqual([{ model: "fast", tokens: 1800, costUsd: 0.002 }]);
  });

  it("keeps log lines with their offset from the first event, and marks warnings", () => {
    nextId = 0;
    const s = foldEvents([
      run("running"),
      ev({ agent: "intake", kind: "log", message: "Parsed 1 file(s)" }),
      ev({ agent: "intake", kind: "log", status: "warning", message: "Dropped a feature" }),
    ]);
    expect(s.rows.intake.logs.map((l) => [l.at, l.tone, l.text])).toEqual([
      [1000, "plain", "Parsed 1 file(s)"],
      [2000, "warn", "Dropped a feature"],
    ]);
  });

  it("fails a step with its error and counts the attempt", () => {
    nextId = 0;
    const s = foldEvents([
      ev({ agent: "port", kind: "status", status: "running", attempt: 3 }),
      ev({
        agent: "port",
        kind: "error",
        status: "failed",
        attempt: 3,
        error: { file: "app/plans/page.tsx", line: 42, message: "Type error", excerpt: "return <PlanList />" },
      }),
    ]);
    expect(s.rows.port.state).toBe("failed");
    expect(s.rows.port.attempt).toBe(3);
    expect(s.rows.port.error).toMatchObject({ file: "app/plans/page.tsx", line: 42 });
  });

  it("shows a budget pause as paused, not failed", () => {
    nextId = 0;
    const s = foldEvents([
      ev({ agent: "architect", kind: "status", status: "running", attempt: 1 }),
      ev({ agent: "architect", kind: "error", status: "paused", attempt: 1, message: "budget" }),
    ]);
    expect(s.rows.architect.state).toBe("paused");
  });

  it("ignores events it has already seen (a replay after a reconnect)", () => {
    nextId = 0;
    const first = ev({ agent: "intake", kind: "log", message: "once" });
    let s = reduceEvent(initialTimeline(), first);
    s = reduceEvent(s, first);
    expect(s.rows.intake.logs).toHaveLength(1);
    expect(s.lastId).toBe(first.id);
  });
});

describe("run status and gates", () => {
  it("follows run-level events only", () => {
    nextId = 0;
    let s = foldEvents([run("queued"), run("running")]);
    expect(s.runStatus).toBe("running");
    s = reduceEvent(s, run("waiting_gate1", "gate"));
    expect(s.runStatus).toBe("waiting_gate1");
    s = reduceEvent(s, ev({ agent: "run", kind: "gate", status: "approve", message: "Gate scope decision" }));
    expect(s.runStatus).toBe("waiting_gate1"); // the verdict alone does not change the status
    s = reduceEvent(s, run("running"));
    expect(s.runStatus).toBe("running");
    s = reduceEvent(s, ev({ agent: "run", kind: "error", status: "failed", error: { message: "boom" } }));
    expect(s.runStatus).toBe("failed");
  });

  it("derives the gate row: idle, waiting, passed, and idle again after a re-extraction", () => {
    nextId = 0;
    let s = foldEvents([
      run("running"),
      ev({ agent: "intelligence", kind: "status", status: "running", attempt: 1 }),
      ev({ agent: "intelligence", kind: "status", status: "done", attempt: 1 }),
    ]);
    expect(gateView(s, "gate1")).toBe("idle");
    s = reduceEvent(s, run("waiting_gate1", "gate"));
    expect(gateView(s, "gate1")).toBe("waiting");
    s = foldEvents(
      [
        run("running"),
        ev({ agent: "gate1", kind: "status", status: "running", attempt: 1 }),
        ev({ agent: "gate1", kind: "status", status: "done", attempt: 1 }),
      ],
      s,
    );
    expect(gateView(s, "gate1")).toBe("passed");
    s = reduceEvent(s, ev({ agent: "intelligence", kind: "status", status: "running", attempt: 2 }));
    expect(gateView(s, "gate1")).toBe("idle");
    expect(s.rows.intelligence.attempt).toBe(2);
  });
});
