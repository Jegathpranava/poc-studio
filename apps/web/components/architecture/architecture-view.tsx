"use client";

import { CircleAlert, Download, Info, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

import { useRun } from "@/components/run/run-context";
import { PageHead } from "@/components/shell/page-head";
import { api, ApiError } from "@/lib/api";
import { labelForUseCase, type Architecture } from "@/lib/architecture";

import { CostTable } from "./cost-table";
import { MermaidDiagram } from "./mermaid-diagram";
import { ModelTable } from "./model-table";

type Load =
  | { state: "loading" }
  | { state: "error"; error: ApiError }
  | { state: "empty" }
  | { state: "ready"; version: number; arch: Architecture };

export function ArchitectureView() {
  const { runId, status } = useRun();
  const [load, setLoad] = useState<Load>({ state: "loading" });
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let live = true;
    api.runs
      .architecture(runId)
      .then(({ version, data }) => live && setLoad({ state: "ready", version, arch: data }))
      .catch((e: unknown) => {
        if (!live) return;
        if (e instanceof ApiError && e.status === 404) setLoad((l) => (l.state === "ready" ? l : { state: "empty" }));
        else setLoad({ state: "error", error: e instanceof ApiError ? e : new ApiError("Unknown error.") });
      });
    return () => {
      live = false;
    };
  }, [runId, status, attempt]);

  const head = (
    <PageHead
      title="Architecture spec"
      description={load.state === "ready" ? `Version ${load.version}, designed by the Solution Architect.` : undefined}
      actions={
        load.state === "ready" ? (
          <a className="btn" href={api.runs.architectureMarkdownUrl(runId)} download>
            <Download className="icon" aria-hidden="true" />
            Download .md
          </a>
        ) : undefined
      }
    />
  );

  if (load.state === "loading") {
    return (
      <section className="screen">
        {head}
        <div className="panel">
          <div className="panel-body stack" aria-busy="true" aria-label="Loading the architecture">
            {[0, 1, 2].map((i) => (
              <span key={i} className="sk" style={{ width: `${95 - i * 15}%` }} />
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (load.state === "error") {
    return (
      <section className="screen">
        {head}
        <div className="banner err" role="alert">
          <CircleAlert className="icon" aria-hidden="true" />
          <div className="grow">
            <b>The architecture could not be loaded.</b>
            <p className="muted">{load.error.message}</p>
            <div className="actions">
              <button type="button" className="btn sm" onClick={() => setAttempt((n) => n + 1)}>
                <RefreshCw className="icon" aria-hidden="true" />
                Try again
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (load.state === "empty") {
    return (
      <section className="screen">
        {head}
        <div className="panel">
          <div className="empty">
            <Info aria-hidden="true" />
            <h2>Available after the Solution Architect runs</h2>
            <p>The architecture appears here once the brief is approved at Gate 1.</p>
          </div>
        </div>
      </section>
    );
  }

  const { arch } = load;
  return (
    <section className="screen">
      {head}
      <div className="grid-2">
        <div className="stack">
          <div className="panel">
            <div className="panel-head">
              <h2>System diagram</h2>
              <span className="tag" data-testid="use-case">
                {labelForUseCase(arch.use_case_class)}
              </span>
            </div>
            <div className="panel-body">
              <MermaidDiagram source={arch.mermaid} label="System diagram of the proposed architecture" />
            </div>
          </div>
          <div className="panel">
            <div className="panel-head">
              <h2>Approach</h2>
            </div>
            <div className="panel-body prose">
              <p>{arch.rationale}</p>
              {arch.phases.length > 0 ? (
                <>
                  <h3>Phases</h3>
                  <ol className="plain-list">
                    {arch.phases.map((p) => (
                      <li key={p.name}>
                        <b>{p.name}</b>{" "}
                        <span className="muted">
                          ({p.weeks} {p.weeks === 1 ? "week" : "weeks"})
                        </span>
                        : {p.detail}
                      </li>
                    ))}
                  </ol>
                </>
              ) : null}
            </div>
          </div>
        </div>
        <div className="stack">
          <div className="panel">
            <div className="panel-head">
              <h2>Model picks</h2>
            </div>
            <ModelTable models={arch.models} />
          </div>
          <div className="panel">
            <div className="panel-head">
              <h2>Monthly cost</h2>
            </div>
            <CostTable cost={arch.monthly_cost} />
            <p className="xs muted panel-body">{arch.monthly_cost.assumptions}</p>
          </div>
        </div>
      </div>
    </section>
  );
}
