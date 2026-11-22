import { Check, Pause, X } from "lucide-react";

import { formatClock, formatCost, formatElapsed, formatTokens, modelLabel } from "@/lib/run-labels";
import type { StepRow } from "@/lib/run-steps";

import { StepError } from "./step-error";
import { stepInfo, stepSummary } from "./step-info";

const CLASS: Record<StepRow["state"], string> = {
  idle: "",
  active: "active",
  done: "done",
  failed: "fail",
  paused: "wait",
};

function elapsed(row: StepRow, now: number): string {
  if (!row.startedAt) return "-";
  const end = row.finishedAt ? Date.parse(row.finishedAt) : now;
  return formatElapsed(end - Date.parse(row.startedAt));
}

export function PipelineStep({ agent, row, now }: { agent: string; row: StepRow; now: number }) {
  const info = stepInfo(agent);
  const Icon = row.state === "done" ? Check : row.state === "failed" ? X : row.state === "paused" ? Pause : info.icon;
  const started = row.state !== "idle";
  const showAttempt = row.attempt > 1 || (row.state === "failed" && row.error !== null);
  const sub = started ? stepSummary(row, "Working") : info.waiting;

  return (
    <div className={`step ${CLASS[row.state]}`.trim()} data-agent={agent} data-state={row.state}>
      <span className="node">
        <Icon aria-hidden="true" />
      </span>
      <div className="step-body">
        <div className="step-title">
          {info.title}
          {info.tag ? <span className="tag">{info.tag}</span> : null}
          {showAttempt ? (
            <span className={`tag attempt${row.state === "failed" ? " fail" : ""}`}>Attempt {row.attempt} of 3</span>
          ) : null}
        </div>
        {row.state !== "failed" || !row.error ? <div className="step-sub">{sub}</div> : null}
        {row.error && row.state === "failed" ? <StepError error={row.error} /> : null}
        {row.logs.length > 0 ? (
          <details className="steplog">
            <summary>Output log, {row.logs.length} lines</summary>
            <div className="log">
              {row.logs.map((line, i) => (
                <div key={i} className={line.tone === "err" ? "errline" : undefined}>
                  <span className="t">{formatClock(line.at)}</span>
                  <span className={line.tone === "plain" ? undefined : line.tone}>{line.text}</span>
                </div>
              ))}
            </div>
          </details>
        ) : null}
      </div>
      <div className="step-meta">
        {started ? (
          <>
            <span>{elapsed(row, now)}</span>
            <span>{formatTokens(row.tokensIn + row.tokensOut)} tok</span>
            <span className="cost">
              {formatCost(row.costUsd)} / {modelLabel(row.model)}
            </span>
          </>
        ) : (
          <span>-</span>
        )}
      </div>
    </div>
  );
}
