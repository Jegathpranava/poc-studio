import type { FileNode, PublishOptions, QaReport, RunDetail } from "./api";

/** GitHub account that owns generated client repos (spec amendment 6). */
export const REPO_OWNER = "Jegathpranava";
export const REPO_NAME_PATTERN = /^[A-Za-z0-9._-]{1,100}$/;

/** A message for a repo name GitHub or the API would reject, or null when it is fine. */
export function validateRepoName(name: string): string | null {
  if (name.length === 0) return "Give the repository a name.";
  if (name.length > 100) return "Use 100 characters or fewer.";
  if (!REPO_NAME_PATTERN.test(name)) return "Use letters, numbers, dots, dashes and underscores only.";
  if (name === "." || name === "..") return "That name is not allowed.";
  if (name.endsWith(".git")) return "A name cannot end with .git.";
  return null;
}

function slug(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

/** Mirrors the API default: the client and title slug plus `-poc`. */
export function defaultRepoName(client: string, title: string): string {
  const c = slug(client) || "client";
  const t = slug(title).replace(/-poc$/, "") || "prototype";
  const base = t.startsWith(c) ? t : `${c}-${t}`;
  return `${base.slice(0, 90).replace(/-+$/, "")}-poc`;
}

export function repoPath(name: string): string {
  return `${REPO_OWNER}/${name}`;
}

export interface QaView {
  total: number;
  passed: number;
  blocked: boolean;
  buildFailed: boolean;
  deckMissing: boolean;
  sentBack: string | null;
}

const COUNT_WORDS = ["", "once", "twice"];

export function qaView(report: QaReport): QaView {
  const failed = (name: string) => report.checks.some((c) => c.name === name && !c.ok);
  const n = report.sent_back_count;
  return {
    total: report.checks.length,
    passed: report.checks.filter((c) => c.ok).length,
    blocked: report.block_publish,
    buildFailed: failed("build_passed"),
    deckMissing: failed("deck_present"),
    sentBack: n > 0 ? `Sent back ${COUNT_WORDS[n] ?? `${n} times`}: QA returned work to its agent to fix, then checked again.` : null,
  };
}

export function canPublish(report: QaReport | null, nameError: string | null, busy: boolean): boolean {
  return report !== null && !report.block_publish && nameError === null && !busy;
}

function countFiles(nodes: FileNode[]): number {
  return nodes.reduce((n, f) => n + (f.type === "dir" ? countFiles(f.children ?? []) : 1), 0);
}

/** The prototype files plus the README, `.env.example`, docs and deck the publish adds. An estimate. */
export function estimateFileCount(tree: FileNode[] | null, options: PublishOptions, hasVideo: boolean): number | null {
  if (tree === null) return null;
  return countFiles(tree) + 1 + 1 + (options.add_ci ? 1 : 0) + 2 + 1 + (hasVideo ? 1 : 0);
}

export function formatDuration(ms: number): string {
  const total = Math.max(0, Math.round(ms / 1000));
  const m = Math.floor(total / 60);
  const s = total % 60;
  return m > 0 ? `${m}m ${s}s` : `${s}s`;
}

export interface RunTimes {
  agentMs: number | null;
  gateMs: number | null;
}

function ts(value: string | null | undefined): number | null {
  const t = value ? Date.parse(value) : NaN;
  return Number.isNaN(t) ? null : t;
}

/**
 * Agent time is the wall clock from the run start to Gate 2 ready, minus the time waiting at Gate 1.
 * A gate wait is the gap between the step before the gate finishing and the gate step starting.
 */
export function runTimes(detail: RunDetail): RunTimes {
  const started = ts(detail.started_at);
  const steps = detail.steps;
  const last = (agent: string) =>
    steps.filter((s) => s.agent === agent).sort((a, b) => (ts(b.finished_at) ?? 0) - (ts(a.finished_at) ?? 0))[0];
  const gap = (before: string, gate: string): number => {
    const a = ts(last(before)?.finished_at);
    const g = steps.find((s) => s.agent === gate);
    const b = ts(g?.started_at);
    return a !== null && b !== null && b > a ? b - a : 0;
  };
  const qaDone = ts(last("qa")?.finished_at);
  const gate1 = gap("intelligence", "gate1");
  const gate2 = gap("qa", "gate2");
  return {
    agentMs: started !== null && qaDone !== null ? Math.max(0, qaDone - started - gate1) : null,
    gateMs: steps.some((s) => s.agent === "gate1") ? gate1 + gate2 : null,
  };
}
