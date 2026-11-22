import type { RunStatus } from "./api";

export type RerunReason = "revise" | "send_back" | "retry";

/** SSE `data` payload (spec 7b). */
export interface EventError {
  file?: string | null;
  line?: number | null;
  col?: number | null;
  message: string;
  excerpt?: string | null;
}

export interface RunEvent {
  id: number;
  ts: string;
  run_id: string;
  agent: string;
  kind: "status" | "log" | "cost" | "gate" | "error";
  status?: string | null;
  message?: string | null;
  model?: string | null;
  tokens_in?: number | null;
  tokens_out?: number | null;
  cost_usd?: number | null;
  attempt?: number | null;
  /** On a rerun's "running" event: why it started. */
  reason?: RerunReason | null;
  error?: EventError | null;
}

/** Spec 7b order. The two gates are rows too, so they can cut across the rail. */
export const STAGES = [
  "intake",
  "intelligence",
  "gate1",
  "architect",
  "screens",
  "pitch",
  "port",
  "assemble",
  "qa",
  "gate2",
  "video",
  "repo",
] as const;
export type Stage = (typeof STAGES)[number];

export type StepState = "idle" | "active" | "done" | "failed" | "paused";
export type LogTone = "plain" | "ok" | "warn" | "err";

export interface LogLine {
  /** Milliseconds since the first event of the run. */
  at: number;
  tone: LogTone;
  text: string;
}

export interface StepRow {
  agent: string;
  state: StepState;
  /** Step runs so far (the build attempt of a port while it builds). */
  attempt: number;
  /** Build attempts of the Prototype Builder, 1 to 3. Zero before its first build. */
  buildAttempt: number;
  /** Reruns caused by a Gate 2 revision or a QA send-back. */
  revision: number;
  reason: RerunReason | null;
  model: string | null;
  tokensIn: number;
  tokensOut: number;
  costUsd: number;
  startedAt: string | null;
  finishedAt: string | null;
  logs: LogLine[];
  error: EventError | null;
}

export interface TimelineState {
  lastId: number;
  firstTs: number | null;
  runStatus: RunStatus | null;
  rows: Record<string, StepRow>;
}

const RUN_STATUSES: readonly string[] = [
  "queued",
  "running",
  "waiting_gate1",
  "waiting_gate2",
  "paused_budget",
  "failed",
  "delivered",
];

export function emptyRow(agent: string): StepRow {
  return {
    agent,
    state: "idle",
    attempt: 0,
    buildAttempt: 0,
    revision: 0,
    reason: null,
    model: null,
    tokensIn: 0,
    tokensOut: 0,
    costUsd: 0,
    startedAt: null,
    finishedAt: null,
    logs: [],
    error: null,
  };
}

export function initialTimeline(): TimelineState {
  return { lastId: 0, firstTs: null, runStatus: null, rows: {} };
}

function runLevel(state: TimelineState, ev: RunEvent): RunStatus | null {
  const s = ev.status ?? "";
  if (ev.kind === "status" && RUN_STATUSES.includes(s)) return s as RunStatus;
  if (ev.kind === "gate" && (s === "waiting_gate1" || s === "waiting_gate2")) return s;
  if (ev.kind === "error" && s === "failed") return "failed";
  return state.runStatus;
}

/** Folds one SSE event into the timeline. Ids at or below `lastId` are ignored (replay after a reconnect). */
export function reduceEvent(state: TimelineState, ev: RunEvent): TimelineState {
  if (ev.id <= state.lastId) return state;
  const ts = Date.parse(ev.ts);
  const firstTs = state.firstTs ?? ts;
  const next: TimelineState = { ...state, lastId: ev.id, firstTs };
  const at = ts - firstTs;

  if (ev.agent === "run") {
    next.runStatus = runLevel(state, ev);
    return next;
  }

  const prev = state.rows[ev.agent] ?? emptyRow(ev.agent);
  const row: StepRow = { ...prev, logs: [...prev.logs] };
  const push = (tone: LogTone, text: string) => row.logs.push({ at, tone, text });

  if (ev.kind === "status") {
    if (ev.status === "running") {
      row.state = "active";
      row.attempt = ev.attempt ?? row.attempt + 1;
      row.reason = ev.reason ?? null;
      if (ev.reason === "revise" || ev.reason === "send_back") row.revision += 1;
      row.buildAttempt = 0;
      row.model = ev.model ?? row.model;
      row.startedAt = row.startedAt ?? ev.ts;
      row.finishedAt = null;
      row.error = null;
      push("plain", row.revision > 0 && row.reason !== "retry" ? `started, revision ${row.revision}` : `started, run ${row.attempt}`);
    } else if (ev.status === "done") {
      row.state = "done";
      row.finishedAt = ev.ts;
      push("ok", "ok    finished");
    }
  } else if (ev.kind === "log") {
    if (ev.agent === "port" && ev.attempt) row.buildAttempt = ev.attempt;
    push(ev.status === "warning" ? "warn" : "plain", ev.message ?? "");
  } else if (ev.kind === "cost") {
    row.model = ev.model ?? row.model;
    row.tokensIn += ev.tokens_in ?? 0;
    row.tokensOut += ev.tokens_out ?? 0;
    row.costUsd += ev.cost_usd ?? 0;
  } else if (ev.kind === "error") {
    row.state = ev.status === "paused" ? "paused" : "failed";
    row.finishedAt = ev.ts;
    row.attempt = ev.attempt ?? row.attempt;
    if (ev.agent === "port" && ev.attempt) row.buildAttempt = ev.attempt;
    row.error = ev.error ?? { message: ev.message ?? "The step failed." };
    push("err", `err   ${row.error.message}`);
  }

  next.rows = { ...state.rows, [ev.agent]: row };
  // A re-extraction sends the owner back to Gate 1, so the passed gate no longer counts.
  if (ev.agent === "intelligence" && ev.kind === "status" && ev.status === "running" && next.rows.gate1) {
    next.rows = { ...next.rows, gate1: emptyRow("gate1") };
  }
  return next;
}

/**
 * The tag next to a step title. "Attempt X of 3" counts the Prototype Builder's build attempts only; a rerun
 * caused by a Gate 2 revision or a QA send-back reads "Revision N" and is never shown as a failure.
 */
export function stepTag(agent: string, row: StepRow): { label: string; fail: boolean } | null {
  if (agent === "port" && (row.buildAttempt > 1 || (row.state === "failed" && row.error !== null))) {
    return { label: `Attempt ${row.buildAttempt || row.attempt} of 3`, fail: row.state === "failed" };
  }
  if (row.revision > 0) return { label: `Revision ${row.revision}`, fail: false };
  return null;
}

export function foldEvents(events: RunEvent[], from: TimelineState = initialTimeline()): TimelineState {
  return events.reduce(reduceEvent, from);
}

export type GateView = "passed" | "waiting" | "idle";

/** A gate row is "waiting" only while the run is parked on it. */
export function gateView(state: TimelineState, gate: "gate1" | "gate2"): GateView {
  const waiting = gate === "gate1" ? "waiting_gate1" : "waiting_gate2";
  if (state.runStatus === waiting) return "waiting";
  return state.rows[gate]?.state === "done" ? "passed" : "idle";
}

export function totals(state: TimelineState): { tokens: number; costUsd: number } {
  return Object.values(state.rows).reduce(
    (acc, r) => ({ tokens: acc.tokens + r.tokensIn + r.tokensOut, costUsd: acc.costUsd + r.costUsd }),
    { tokens: 0, costUsd: 0 },
  );
}

export function costByModel(state: TimelineState): { model: string; tokens: number; costUsd: number }[] {
  const by = new Map<string, { tokens: number; costUsd: number }>();
  for (const r of Object.values(state.rows)) {
    if (!r.model || (r.tokensIn + r.tokensOut === 0 && r.costUsd === 0)) continue;
    const cur = by.get(r.model) ?? { tokens: 0, costUsd: 0 };
    by.set(r.model, { tokens: cur.tokens + r.tokensIn + r.tokensOut, costUsd: cur.costUsd + r.costUsd });
  }
  return [...by].map(([model, v]) => ({ model, ...v }));
}
