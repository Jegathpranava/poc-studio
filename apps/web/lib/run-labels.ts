import type { RunStatus } from "./api";

export type Tone = "run" | "wait" | "done" | "fail";

export const STATUS_LABELS: Record<RunStatus, string> = {
  queued: "Queued",
  running: "Running",
  waiting_gate1: "Waiting at Gate 1",
  waiting_gate2: "Waiting at Gate 2",
  paused_budget: "Paused at the budget limit",
  failed: "Needs attention",
  delivered: "Delivered",
};

const TONES: Record<RunStatus, Tone> = {
  queued: "run",
  running: "run",
  waiting_gate1: "wait",
  waiting_gate2: "wait",
  paused_budget: "wait",
  failed: "fail",
  delivered: "done",
};

export function statusLabel(status: RunStatus): string {
  return STATUS_LABELS[status];
}

export function statusTone(status: RunStatus): Tone {
  return TONES[status];
}

const MODEL_LABELS: Record<string, string> = {
  fast: "Ollama fast",
  smart: "Ollama smart",
  "claude-haiku-5-5": "Haiku 5.5",
};

export function modelLabel(model: string | null | undefined): string {
  if (!model) return "no model";
  return MODEL_LABELS[model] ?? model;
}

export function formatTokens(n: number): string {
  return n < 1000 ? `${n}` : `${(n / 1000).toFixed(1)}k`;
}

export function formatCost(usd: number): string {
  return `$${usd.toFixed(3)}`;
}

/** 83000 ms becomes "1m 23s"; under a minute it is "23s". */
export function formatElapsed(ms: number): string {
  const total = Math.max(0, Math.round(ms / 1000));
  const m = Math.floor(total / 60);
  return m > 0 ? `${m}m ${String(total % 60).padStart(2, "0")}s` : `${total}s`;
}

/** The "00:22" offset shown in step logs. */
export function formatClock(ms: number): string {
  const total = Math.max(0, Math.round(ms / 1000));
  return `${String(Math.floor(total / 60)).padStart(2, "0")}:${String(total % 60).padStart(2, "0")}`;
}
