import type { RunSummary } from "@/lib/api";

export type StatusTone = "run" | "wait" | "done" | "fail";
export type StatusFilter = "all" | "wait" | "done";

export const PLACEHOLDER = "--";

export function statusView(run: RunSummary): { tone: StatusTone; label: string } {
  switch (run.status) {
    case "queued":
    case "running":
      return { tone: "run", label: "Running" };
    case "waiting_gate1":
      return { tone: "wait", label: "Gate 1: review brief" };
    case "waiting_gate2":
      return { tone: "wait", label: "Gate 2: publish" };
    case "paused_budget":
      return { tone: "wait", label: "Paused: budget" };
    case "failed":
      return { tone: "fail", label: "Needs attention" };
    case "delivered":
      return { tone: "done", label: "Delivered" };
  }
}

export function matchesFilter(run: RunSummary, filter: StatusFilter): boolean {
  if (filter === "all") return true;
  const { tone } = statusView(run);
  return filter === "wait" ? tone === "wait" : tone === "done";
}

export function matchesQuery(run: RunSummary, query: string): boolean {
  const q = query.trim().toLowerCase();
  if (!q) return true;
  return `${run.client_name} ${run.sector ?? ""} ${run.title}`.toLowerCase().includes(q);
}

export function durationMs(run: RunSummary): number | null {
  if (!run.started_at || !run.finished_at) return null;
  const ms = Date.parse(run.finished_at) - Date.parse(run.started_at);
  return Number.isFinite(ms) && ms >= 0 ? ms : null;
}

export function formatDuration(ms: number | null): string {
  if (ms === null) return PLACEHOLDER;
  const total = Math.round(ms / 1000);
  return `${Math.floor(total / 60)}m ${String(total % 60).padStart(2, "0")}s`;
}

export function formatUsd(value: number): string {
  return `$${value.toFixed(2)}`;
}

export function formatWhen(iso: string | null | undefined, now: number = Date.now()): string {
  if (!iso) return PLACEHOLDER;
  const diff = now - Date.parse(iso);
  if (!Number.isFinite(diff)) return PLACEHOLDER;
  const min = Math.floor(diff / 60_000);
  if (min < 1) return "Just now";
  if (min < 60) return `${min} min ago`;
  const hours = Math.floor(min / 60);
  if (hours < 24) return `${hours} h ago`;
  const days = Math.floor(hours / 24);
  return days === 1 ? "Yesterday" : `${days} days ago`;
}
