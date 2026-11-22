import { describe, expect, it } from "vitest";

import type { RunStatus } from "@/lib/api";
import { formatClock, formatCost, formatElapsed, formatTokens, modelLabel, statusLabel, statusTone } from "@/lib/run-labels";

describe("status labels", () => {
  it("names every run status", () => {
    const expected: Record<RunStatus, [string, string]> = {
      queued: ["Queued", "run"],
      running: ["Running", "run"],
      waiting_gate1: ["Waiting at Gate 1", "wait"],
      waiting_gate2: ["Waiting at Gate 2", "wait"],
      paused_budget: ["Paused at the budget limit", "wait"],
      failed: ["Needs attention", "fail"],
      delivered: ["Delivered", "done"],
    };
    for (const [status, [label, tone]] of Object.entries(expected) as [RunStatus, [string, string]][]) {
      expect(statusLabel(status)).toBe(label);
      expect(statusTone(status)).toBe(tone);
    }
  });
});

describe("model labels", () => {
  it("maps the gateway model ids", () => {
    expect(modelLabel("fast")).toBe("Ollama fast");
    expect(modelLabel("smart")).toBe("Ollama smart");
    expect(modelLabel("claude-haiku-5-5")).toBe("Haiku 5.5");
  });

  it("falls back to the raw id, or a placeholder", () => {
    expect(modelLabel("some-new-model")).toBe("some-new-model");
    expect(modelLabel(null)).toBe("no model");
  });
});

describe("number formats", () => {
  it("formats tokens, cost and time", () => {
    expect(formatTokens(812)).toBe("812");
    expect(formatTokens(24100)).toBe("24.1k");
    expect(formatCost(0)).toBe("$0.000");
    expect(formatCost(0.0102)).toBe("$0.010");
    expect(formatElapsed(31_000)).toBe("31s");
    expect(formatElapsed(72_000)).toBe("1m 12s");
    expect(formatClock(22_000)).toBe("00:22");
  });
});
