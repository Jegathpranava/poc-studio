"use client";

import { useCallback, useEffect, useReducer, useRef, useState } from "react";

import { BASE_URL } from "@/lib/api";
import { initialTimeline, reduceEvent, type RunEvent, type TimelineState } from "@/lib/run-steps";

/** `failed`: the stream never delivered an event and connecting failed repeatedly, so retrying stopped. */
export type Connection = "connecting" | "live" | "reconnecting" | "failed";

const BACKOFF_MS = [1000, 2000, 4000, 8000, 15000];
/** Consecutive failed connects, with no event ever received, before the hook gives up. */
export const MAX_FIRST_FAILURES = 3;

export function backoffDelay(attempt: number): number {
  return BACKOFF_MS[Math.min(attempt, BACKOFF_MS.length - 1)];
}

/** `after` is only added on manual reconnects: EventSource sends Last-Event-ID by itself on its own. */
export function eventsUrl(runId: string, lastId: number): string {
  const base = `${BASE_URL}/api/runs/${runId}/events`;
  return lastId > 0 ? `${base}?after=${lastId}` : base;
}

interface Options {
  /** True when the run is known not to exist (the detail fetch answered 404): do not connect at all. */
  halt?: boolean;
}

/**
 * Subscribes to /api/runs/{id}/events. The API replays the run and then streams live. The browser retries
 * dropped connections by itself; when the stream closes with an error the hook reconnects with a backoff,
 * passing the last seen id. With no event ever received it stops after MAX_FIRST_FAILURES failed connects
 * and reports `failed`; `retry` starts over. Replays are harmless because the reducer skips seen ids.
 */
export function useRunEvents(
  runId: string,
  { halt = false }: Options = {},
): { timeline: TimelineState; connection: Connection; retry: () => void } {
  const [timeline, dispatch] = useReducer(reduceEvent, undefined, initialTimeline);
  const [connection, setConnection] = useState<Connection>("connecting");
  const [round, setRound] = useState(0);
  const lastId = useRef(0);

  const retry = useCallback(() => {
    setConnection("connecting");
    setRound((n) => n + 1);
  }, []);

  useEffect(() => {
    if (halt) return;
    let source: EventSource | null = null;
    let timer: ReturnType<typeof setTimeout> | undefined;
    let failures = 0; // consecutive, for the backoff
    let firstFailures = 0; // failed connects while no event has ever arrived
    let stopped = false;

    const onMessage = (msg: MessageEvent<string>) => {
      try {
        const ev = JSON.parse(msg.data) as RunEvent;
        lastId.current = Math.max(lastId.current, ev.id);
        firstFailures = 0;
        dispatch(ev);
      } catch {
        // A malformed frame is skipped; the next one still applies.
      }
    };

    const connect = () => {
      const es = new EventSource(eventsUrl(runId, lastId.current));
      source = es;
      es.onopen = () => {
        failures = 0;
        setConnection("live");
      };
      es.addEventListener("step", onMessage as EventListener);
      es.addEventListener("run", onMessage as EventListener);
      es.onerror = () => {
        if (stopped) return;
        if (lastId.current === 0 && ++firstFailures >= MAX_FIRST_FAILURES) {
          stopped = true;
          es.close();
          setConnection("failed");
          return;
        }
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
  }, [runId, halt, round]);

  return { timeline, connection, retry };
}
