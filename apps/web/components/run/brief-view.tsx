"use client";

import { CircleAlert, Info, RefreshCw } from "lucide-react";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useRef, useState } from "react";

import { PageHead } from "@/components/shell/page-head";
import { notify } from "@/components/shell/notify";
import { api, ApiError } from "@/lib/api";
import { fromRequirements, toRequirements, unconfirmedCount, validateForm, type BriefForm } from "@/lib/brief-form";
import type { Requirements } from "@/lib/requirements";

import { BriefFeatures } from "./brief-features";
import { BriefGoalsPanel } from "./brief-goals-panel";
import { BriefSide } from "./brief-side";
import { GateActionBar } from "./gate-action-bar";
import { RequestChanges } from "./request-changes";
import { useRun } from "./run-context";

type Load =
  | { state: "loading" }
  | { state: "error"; error: ApiError }
  | { state: "empty" }
  | { state: "ready"; version: number; base: Requirements };

function describe(error: unknown): string[] {
  if (error instanceof ApiError && error.fields.length > 0) {
    return error.fields.map((f) => `${f.loc.join(" > ")}: ${f.msg}`);
  }
  return [error instanceof Error ? error.message : "Something went wrong."];
}

export function BriefView() {
  const { runId, status, reload } = useRun();
  const router = useRouter();
  const [load, setLoad] = useState<Load>({ state: "loading" });
  const [form, setForm] = useState<BriefForm | null>(null);
  const [problems, setProblems] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [noteOpen, setNoteOpen] = useState(false);
  const [noteError, setNoteError] = useState<string | null>(null);
  const [attempt, setAttempt] = useState(0);
  const version = useRef(0);

  // Load the latest brief; again whenever the run status changes, since a re-extraction adds a version.
  useEffect(() => {
    let live = true;
    api.runs
      .requirements(runId)
      .then(({ version: v, data }) => {
        if (!live || v === version.current) return; // same version: keep the owner's unsaved edits
        version.current = v;
        setLoad({ state: "ready", version: v, base: data });
        setForm(fromRequirements(data));
        setProblems([]);
      })
      .catch((e: unknown) => {
        if (!live) return;
        if (e instanceof ApiError && e.status === 404) setLoad((l) => (l.state === "ready" ? l : { state: "empty" }));
        else setLoad({ state: "error", error: e instanceof ApiError ? e : new ApiError("Unknown error.") });
      });
    return () => {
      live = false;
    };
  }, [runId, status, attempt]);

  const patch = useCallback((p: Partial<BriefForm>) => setForm((f) => (f ? { ...f, ...p } : f)), []);
  const editable = status === "waiting_gate1";

  const approve = async () => {
    if (load.state !== "ready" || !form) return;
    const found = validateForm(form);
    setProblems(found);
    if (found.length > 0) return;
    setBusy(true);
    try {
      await api.runs.decideScope(runId, { decision: "approve", edits: toRequirements(load.base, form) });
      notify.success("Brief approved", "The architecture step is starting.");
      reload();
      router.push(`/runs/${runId}`);
    } catch (e) {
      setProblems(describe(e));
    } finally {
      setBusy(false);
    }
  };

  const reextract = async (note: string) => {
    setBusy(true);
    setNoteError(null);
    try {
      await api.runs.decideScope(runId, { decision: "changes", note });
      setNoteOpen(false);
      notify.success("Re-extracting", "A new brief version will appear here.");
      reload();
    } catch (e) {
      setNoteError(describe(e).join(" "));
    } finally {
      setBusy(false);
    }
  };

  const head = (
    <PageHead
      title="Review the brief"
      description="Nothing is designed or built until you approve. Edit anything that is wrong; this is the cheapest place to fix it."
    />
  );

  if (load.state === "loading") {
    return (
      <section className="screen">
        {head}
        <div className="panel">
          <div className="panel-body stack" aria-busy="true" aria-label="Loading the brief">
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
            <b>The brief could not be loaded.</b>
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

  if (load.state === "empty" || !form) {
    return (
      <section className="screen">
        {head}
        <div className="panel">
          <div className="empty">
            <Info aria-hidden="true" />
            <h2>No brief yet</h2>
            <p>Meeting Intelligence is still reading the transcript. The brief appears here when it finishes.</p>
          </div>
        </div>
      </section>
    );
  }

  return (
    <section className="screen">
      {head}
      <p className="small note-box" data-testid="brief-version">
        Brief v{load.version}, extracted from the uploaded files.
      </p>
      {!editable ? (
        <div className="banner note" role="note">
          <Info className="icon" aria-hidden="true" />
          <div className="grow">
            This brief is read-only because the run is not waiting at Gate 1.
          </div>
        </div>
      ) : null}
      {problems.length > 0 ? (
        <div className="banner err" role="alert">
          <CircleAlert className="icon" aria-hidden="true" />
          <div className="grow">
            <b>The brief cannot be approved yet.</b>
            <ul className="plain-list">
              {problems.map((p) => (
                <li key={p}>{p}</li>
              ))}
            </ul>
          </div>
        </div>
      ) : null}
      <fieldset className="fieldset-plain" disabled={!editable || busy}>
        <div className="grid-2">
          <div className="stack">
            <BriefGoalsPanel form={form} onChange={patch} />
            <BriefFeatures features={form.features} readOnly={!editable} onChange={patch} />
          </div>
          <BriefSide base={load.base} form={form} onChange={patch} />
        </div>
      </fieldset>
      {editable ? (
        <GateActionBar
          unconfirmed={unconfirmedCount(form)}
          busy={busy}
          onReextract={() => setNoteOpen(true)}
          onApprove={approve}
        />
      ) : null}
      <RequestChanges
        open={noteOpen}
        title="Re-extract with a note"
        description="Meeting Intelligence reads the transcript again and applies your note. You review the new version."
        placeholder="For example: SMS reminders matter more than the app. Treat the US data rule as unconfirmed."
        sendLabel="Re-extract"
        busy={busy}
        error={noteError}
        onCancel={() => setNoteOpen(false)}
        onSend={reextract}
      />
    </section>
  );
}
