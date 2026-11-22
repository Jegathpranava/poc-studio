"use client";

import { CircleAlert, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

import { PageHead } from "@/components/shell/page-head";
import { formatUsd, formatWhen } from "@/components/runs/format";
import { formatCost, formatTokens } from "@/lib/run-labels";
import { STAGES, emptyRow, gateView, totals } from "@/lib/run-steps";

import { CostByModel } from "./cost-by-model";
import { GateRow } from "./gate-row";
import { NextForYou } from "./next-for-you";
import { PipelineStep } from "./pipeline-step";
import { useRun } from "./run-context";

function Skeleton() {
  return (
    <div className="panel-body stack" aria-busy="true" aria-label="Loading the timeline">
      {[0, 1, 2, 3].map((i) => (
        <span key={i} className="sk" style={{ width: `${90 - i * 12}%` }} />
      ))}
    </div>
  );
}

export function TimelineView() {
  const { runId, detail, detailError, status, timeline, connection, reload, reconnect } = useRun();
  const [now, setNow] = useState(() => Date.now());
  const hasEvents = timeline.lastId > 0;
  const running = Object.values(timeline.rows).some((r) => r.state === "active");

  useEffect(() => {
    if (!running) return;
    const t = setInterval(() => setNow(Date.now()), 1000);
    return () => clearInterval(t);
  }, [running]);

  if (detailError && !hasEvents) {
    const missing = detailError.status === 404;
    return (
      <section className="screen">
        <PageHead title={missing ? "Run not found" : "Run"} />
        <div className="banner err" role="alert">
          <CircleAlert className="icon" aria-hidden="true" />
          <div className="grow">
            <b>{missing ? "This run was not found" : "The PoC Studio API is not answering on port 8000."}</b>
            <p className="muted">
              {missing ? `There is no run ${runId}. It may have been deleted, or the link is wrong.` : "Start it with npm run dev, then try again."}
            </p>
            <div className="actions">
              <button type="button" className="btn sm" onClick={reload}>
                <RefreshCw className="icon" aria-hidden="true" />
                Try again
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (connection === "failed" && !hasEvents) {
    return (
      <section className="screen">
        <PageHead title={detail?.title ?? "Run"} />
        <div className="banner err" role="alert">
          <CircleAlert className="icon" aria-hidden="true" />
          <div className="grow">
            <b>Lost connection. Try again</b>
            <p className="muted">The live stream did not answer. Check that the API is running on port 8000.</p>
            <div className="actions">
              <button type="button" className="btn sm" onClick={reconnect}>
                <RefreshCw className="icon" aria-hidden="true" />
                Try again
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  const sum = totals(timeline);
  const budget = detail?.budget_usd;

  return (
    <section className="screen">
      <PageHead
        title={detail?.title ?? "Run"}
        description={detail?.started_at ? `Started ${formatWhen(detail.started_at)}` : undefined}
      />
      {connection === "reconnecting" ? (
        <div className="banner err" role="status">
          <CircleAlert className="icon" aria-hidden="true" />
          <div className="grow">Lost the live connection. Reconnecting.</div>
        </div>
      ) : null}
      <div className="grid-2">
        <div className="panel">
          <div className="panel-head">
            <h2>Agents</h2>
            <span className="xs muted mono num">
              {formatTokens(sum.tokens)} tokens &nbsp;{formatCost(sum.costUsd)}
              {budget !== undefined ? ` of ${formatUsd(budget)}` : ""}
            </span>
          </div>
          {!hasEvents ? (
            connection === "connecting" ? (
              <Skeleton />
            ) : (
              <div className="empty">
                <h2>Waiting for the first event</h2>
                <p>The run is queued. Steps appear here as soon as an agent starts.</p>
              </div>
            )
          ) : (
            <div className="pipeline">
              {STAGES.map((stage) =>
                stage === "gate1" || stage === "gate2" ? (
                  <GateRow key={stage} gate={stage} view={gateView(timeline, stage)} runId={runId} />
                ) : (
                  <PipelineStep
                    key={stage}
                    agent={stage}
                    row={timeline.rows[stage] ?? emptyRow(stage)}
                    now={now}
                    runId={runId}
                    runStatus={status}
                  />
                ),
              )}
            </div>
          )}
        </div>
        <div className="stack">
          <CostByModel state={timeline} />
          <NextForYou status={status} runId={runId} />
        </div>
      </div>
    </section>
  );
}
