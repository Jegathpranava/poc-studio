"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from "react";

import { api, ApiError, type RunDetail, type RunStatus } from "@/lib/api";
import type { TimelineState } from "@/lib/run-steps";

import { useRunEvents, type Connection } from "./use-run-events";

interface RunContextValue {
  runId: string;
  detail: RunDetail | null;
  detailError: ApiError | null;
  /** Live status: the latest run-level event, or the fetched detail until one arrives. */
  status: RunStatus | null;
  timeline: TimelineState;
  connection: Connection;
  reload: () => void;
  /** Reconnect the live stream after it gave up. */
  reconnect: () => void;
}

const RunContext = createContext<RunContextValue | null>(null);

export function RunProvider({ runId, children }: { runId: string; children: ReactNode }) {
  const [detail, setDetail] = useState<RunDetail | null>(null);
  const [detailError, setDetailError] = useState<ApiError | null>(null);
  const { timeline, connection, retry } = useRunEvents(runId, { halt: detailError?.status === 404 });
  const [tick, setTick] = useState(0);

  const status = timeline.runStatus ?? detail?.status ?? null;

  // Refetch the detail when the live status changes, so the title, sector and spend stay current.
  useEffect(() => {
    let live = true;
    api.runs
      .get(runId)
      .then((d) => {
        if (!live) return;
        setDetail(d);
        setDetailError(null);
      })
      .catch((e: unknown) => live && setDetailError(e instanceof ApiError ? e : new ApiError("Unknown error.")));
    return () => {
      live = false;
    };
  }, [runId, timeline.runStatus, tick]);

  const reload = useCallback(() => setTick((n) => n + 1), []);
  const reconnect = useCallback(() => {
    retry();
    setTick((n) => n + 1);
  }, [retry]);

  const value = useMemo(
    () => ({ runId, detail, detailError, status, timeline, connection, reload, reconnect }),
    [runId, detail, detailError, status, timeline, connection, reload, reconnect],
  );
  return <RunContext.Provider value={value}>{children}</RunContext.Provider>;
}

export function useRun(): RunContextValue {
  const ctx = useContext(RunContext);
  if (!ctx) throw new Error("useRun must be used inside <RunProvider>");
  return ctx;
}
