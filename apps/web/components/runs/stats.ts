import type { RunSummary } from "@/lib/api";

import { PLACEHOLDER, durationMs, formatDuration, formatUsd } from "./format";

const WEEK_MS = 7 * 24 * 60 * 60 * 1000;
const HOURS_SAVED_PER_RUN = 5.5;

export interface Stat {
  label: string;
  value: string;
  note?: string;
}

function median(values: number[]): number | null {
  if (values.length === 0) return null;
  const sorted = [...values].sort((a, b) => a - b);
  const mid = Math.floor(sorted.length / 2);
  return sorted.length % 2 ? sorted[mid] : (sorted[mid - 1] + sorted[mid]) / 2;
}

/** Four stats for the strip. Pass null runs for placeholders (loading or no data). */
export function computeStats(runs: RunSummary[] | null, now?: number): Stat[] {
  const empty = !runs || runs.length === 0;
  // Date.now() is read only once data exists: Next 16 forbids reading the clock during prerender.
  const t = empty ? 0 : (now ?? Date.now());
  const thisWeek = empty ? [] : runs.filter((r) => r.started_at && t - Date.parse(r.started_at) <= WEEK_MS);
  const durations = (runs ?? []).map(durationMs).filter((d): d is number => d !== null);
  const avgPaid = empty ? null : runs.reduce((sum, r) => sum + r.paid_usd, 0) / runs.length;

  return [
    { label: "Runs this week", value: empty ? PLACEHOLDER : String(thisWeek.length) },
    { label: "Median time to PoC", value: formatDuration(median(durations)) },
    {
      label: "Hours saved this week",
      value: empty ? PLACEHOLDER : `${Math.round(thisWeek.length * HOURS_SAVED_PER_RUN)} h`,
      note: `at ${HOURS_SAVED_PER_RUN} h per prospect`,
    },
    {
      label: "Paid spend per run",
      value: avgPaid === null ? PLACEHOLDER : formatUsd(avgPaid),
      note: empty ? undefined : `budget ${formatUsd(runs[0].budget_usd)}`,
    },
  ];
}
