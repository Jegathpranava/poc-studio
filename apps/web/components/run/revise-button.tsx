"use client";

import { MessageSquare } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { notify } from "@/components/shell/notify";
import { api, ApiError, type RevisableType } from "@/lib/api";
import { REVISE_INFO, canRequestChanges } from "@/lib/revise";

import { RequestChanges } from "./request-changes";
import { useRun } from "./run-context";

/** "Request changes" for an artifact page: posts the note, toasts who reruns, and goes to the timeline. */
export function ReviseButton({ type }: { type: RevisableType }) {
  const { runId, status } = useRun();
  const router = useRouter();
  const [open, setOpen] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const info = REVISE_INFO[type];
  const enabled = canRequestChanges(status);

  const send = async (note: string) => {
    setBusy(true);
    setError(null);
    try {
      await api.runs.revise(runId, type, note);
      setOpen(false);
      notify.success("Change request sent", `Only ${info.agent} reruns. About ${info.minutes} minutes.`);
      router.push(`/runs/${runId}`);
    } catch (e) {
      setError(e instanceof ApiError ? e.message : "Could not send the change request.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <button
        type="button"
        className="btn"
        onClick={() => setOpen(true)}
        disabled={!enabled}
        title={enabled ? undefined : "Changes can be requested while the run waits at Gate 2"}
      >
        <MessageSquare className="icon" aria-hidden="true" />
        Request changes
      </button>
      <RequestChanges
        open={open}
        title="Request changes"
        description={`Only ${info.agent} reruns, with your note. The steps after it run again; the rest are kept.`}
        sendLabel="Send"
        busy={busy}
        error={error}
        onCancel={() => setOpen(false)}
        onSend={send}
      />
    </>
  );
}
