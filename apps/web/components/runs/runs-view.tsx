"use client";

import { Plus } from "lucide-react";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

import { PageHead } from "@/components/shell/page-head";
import { api, type RunSummary } from "@/lib/api";

import { matchesFilter, matchesQuery, type StatusFilter } from "./format";
import { RunsEmpty } from "./runs-empty";
import { RunsError } from "./runs-error";
import { RunsSkeleton } from "./runs-skeleton";
import { RunsTable } from "./runs-table";
import { RunsToolbar } from "./runs-toolbar";
import { computeStats } from "./stats";
import { StatsStrip } from "./stats-strip";

type Load = { state: "loading" } | { state: "error" } | { state: "ready"; runs: RunSummary[] };

const DESCRIPTION = "Every transcript or requirements doc you have turned into a PoC.";

function NewRunButton() {
  return (
    <Link href="/runs/new" className="btn primary">
      <Plus className="icon" aria-hidden="true" />
      New run
    </Link>
  );
}

export function RunsView() {
  const [load, setLoad] = useState<Load>({ state: "loading" });
  const [attempt, setAttempt] = useState(0);
  const [query, setQuery] = useState("");
  const [filter, setFilter] = useState<StatusFilter>("all");

  useEffect(() => {
    let live = true;
    api.runs
      .list()
      .then((runs) => live && setLoad({ state: "ready", runs }))
      .catch(() => live && setLoad({ state: "error" }));
    return () => {
      live = false;
    };
  }, [attempt]);

  const retry = useCallback(() => {
    setLoad({ state: "loading" });
    setAttempt((n) => n + 1);
  }, []);

  const runs = load.state === "ready" ? load.runs : null;
  const visible = useMemo(
    () => (runs ?? []).filter((r) => matchesFilter(r, filter) && matchesQuery(r, query)),
    [runs, filter, query],
  );

  if (load.state === "error") {
    return (
      <section className="screen">
        <PageHead title="Runs" />
        <RunsError onRetry={retry} />
      </section>
    );
  }

  if (load.state === "ready" && load.runs.length === 0) {
    return (
      <section className="screen">
        <PageHead title="Runs" />
        <RunsEmpty />
      </section>
    );
  }

  return (
    <section className="screen">
      <PageHead title="Runs" description={DESCRIPTION} actions={<NewRunButton />} />
      <StatsStrip stats={computeStats(runs)} />
      {load.state === "loading" ? (
        <RunsSkeleton />
      ) : (
        <div className="panel">
          <RunsToolbar query={query} onQuery={setQuery} filter={filter} onFilter={setFilter} />
          <RunsTable runs={visible} query={query} />
        </div>
      )}
    </section>
  );
}
