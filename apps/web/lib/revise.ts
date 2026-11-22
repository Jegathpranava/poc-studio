import type { RevisableType, RunStatus } from "./api";

/** Who reruns for each artifact page, and roughly how long it takes (shown in the toast). */
export const REVISE_INFO: Record<RevisableType, { agent: string; minutes: number }> = {
  architecture: { agent: "Solution Architect", minutes: 4 },
  prototype: { agent: "Prototype Builder", minutes: 5 },
  deck: { agent: "Pitch and Docs", minutes: 2 },
};

/** Changes can be requested only while the run waits at Gate 2. */
export const canRequestChanges = (status: RunStatus | null): boolean => status === "waiting_gate2";

export type RetryKind = "port" | "resume" | null;

/**
 * Which retry a failed step offers. A failed port build at Gate 2 retries with 3 more attempts or a note;
 * any failed step of a `failed` run offers Resume. Everything else offers nothing.
 */
export function retryKind(agent: string, stepFailed: boolean, status: RunStatus | null): RetryKind {
  if (!stepFailed) return null;
  if (status === "failed") return "resume";
  if (status === "waiting_gate2" && agent === "port") return "port";
  return null;
}

/** Raise offered by the budget banner: double the limit, capped at the API's $1.00 limit. Null when no room is left. */
export function raiseTarget(limitUsd: number): number | null {
  const target = Math.min(1, Math.round(limitUsd * 2 * 100) / 100);
  return target > limitUsd ? target : null;
}
