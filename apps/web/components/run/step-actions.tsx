"use client";

import { MessageSquare, Play, RefreshCw } from "lucide-react";
import { useState } from "react";

import { notify } from "@/components/shell/notify";
import { api, ApiError, type RunStatus } from "@/lib/api";
import { retryKind } from "@/lib/revise";

import { RequestChanges } from "./request-changes";
import { useRun } from "./run-context";

interface Props {
  agent: string;
  failed: boolean;
  runId: string;
  status: RunStatus | null;
}

/** Retry buttons under a failed step: the port build at Gate 2, or Resume for a failed run. */
export function StepActions({ agent, failed, runId, status }: Props) {
  const { reload } = useRun();
  const kind = retryKind(agent, failed, status);
  const [noteOpen, setNoteOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  if (kind === null) return null;

  const run = async (body: { note?: string; attempts?: number }, title: string, description: string) => {
    setBusy(true);
    setError(null);
    try {
      await api.runs.retry(runId, body);
      setNoteOpen(false);
      notify.info(title, description);
      reload();
    } catch (e) {
      const message = e instanceof ApiError ? e.message : "Could not retry.";
      setError(message);
      if (!noteOpen) notify.error("Could not retry", message);
    } finally {
      setBusy(false);
    }
  };

  const gap = { marginTop: "var(--space-3)" };
  if (kind === "resume") {
    return (
      <div className="actions" style={gap}>
        <button
          type="button"
          className="btn sm primary"
          disabled={busy}
          onClick={() => run({}, "Resuming the run", "It continues from the step that stopped.")}
        >
          <Play className="icon" aria-hidden="true" />
          Resume
        </button>
      </div>
    );
  }
  return (
    <>
      <div className="actions" style={gap}>
        <button
          type="button"
          className="btn sm primary"
          disabled={busy}
          onClick={() => run({ attempts: 3 }, "Retrying the build", "Prototype Builder gets 3 more fix attempts.")}
        >
          <RefreshCw className="icon" aria-hidden="true" />
          Retry with 3 more attempts
        </button>
        <button type="button" className="btn sm" disabled={busy} onClick={() => setNoteOpen(true)}>
          <MessageSquare className="icon" aria-hidden="true" />
          Retry with a note
        </button>
      </div>
      <RequestChanges
        open={noteOpen}
        title="Retry with a note"
        description="The Prototype Builder reads your note before it fixes the build error."
        placeholder="For example: plans come from usePlans, not useSessions."
        sendLabel="Retry"
        busy={busy}
        error={error}
        onCancel={() => setNoteOpen(false)}
        onSend={(note) => run({ note, attempts: 3 }, "Retrying the build", "Prototype Builder reads your note.")}
      />
    </>
  );
}
