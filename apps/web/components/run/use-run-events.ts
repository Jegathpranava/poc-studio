"use client";

import { useEffect, useReducer, useState } from "react";

import { BASE_URL } from "@/lib/api";
import { initialTimeline, reduceEvent, type RunEvent, type TimelineState } from "@/lib/run-steps";

export type Connection = "connecting" | "live" | "reconnecting";

const BACKOFF_MS = [1000, 2000, 4000, 8000, 15000];

export function backoffDelay(attempt: number): number {
  return BACKOFF_MS[Math.min(attempt, BACKOFF_MS.length - 1)];
}

/**
 * Subscribes to /api/runs/{id}/events. The API replays the run from the start and then streams live.
 * The browser retries dropped connections by itself; when the server closes the stream with an error
 * the hook reconnects with a backoff. Replays are harmless because the reducer skips ids it has seen.
 */
export function useRunEvents(runId: string): { timeline: TimelineState; connection: Connection } {
  const [timeline, dispatch] = useReducer(reduceEvent, undefined, initialTimeline);
  const [connection, setConnection] = useState<Connection>("connecting");

  useEffect(() => {
    let source: EventSource | null = null;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let failures = 0;
    let stopped = false;

    const onMessage = (msg: MessageEvent<string>) => {
      try {
        dispatch(JSON.parse(msg.data) as RunEvent);
      } catch {
        // A malformed frame is skipped; the next one still applies.
      }
    };

    const connect = () => {
      const es = new EventSource(`${BASE_URL}/api/runs/${runId}/events`);
      source = es;
      es.onopen = () => {
        failures = 0;
        setConnection("live");
      };
      es.addEventListener("step", onMessage as EventListener);
      es.addEventListener("run", onMessage as EventListener);
      es.onerror = () => {
        if (stopped) return;
        setConnection("reconnecting");
        if (es.readyState === EventSource.CLOSED) {
          es.close();
          timer = setTimeout(connect, backoffDelay(failures++));
        }
      };
    };

    connect();
    return () => {
      stopped = true;
      if (timer) clearTimeout(timer);
      source?.close();
    };
  }, [runId]);

  return { timeline, connection };
}
