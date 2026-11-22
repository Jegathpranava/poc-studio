"use client";

import { CircleAlert, RefreshCw, TestTube } from "lucide-react";
import { useCallback, useEffect, useMemo, useState } from "react";

import { ShareActions } from "@/components/share/share-actions";
import { notify } from "@/components/shell/notify";
import { PageHead } from "@/components/shell/page-head";
import { api, ApiError, type FileNode, type PublishOptions, type QaReport, type RunDetail } from "@/lib/api";
import { canPublish, defaultRepoName, estimateFileCount, validateRepoName } from "@/lib/publish";

import { ConfirmPublish } from "./confirm-publish";
import { PublishBar } from "./publish-bar";
import { QaReportPanel } from "./qa-report";
import { RepoPanel } from "./repo-panel";
import { RunStats } from "./run-stats";

type Qa = { state: "loading" } | { state: "error"; message: string } | { state: "ready"; report: QaReport };

interface Props {
  runId: string;
  detail: RunDetail;
  /** Called once the approval was accepted, so the page can follow the publish. */
  onSubmitted: () => void;
}

export function Gate2View({ runId, detail, onSubmitted }: Props) {
  const [qa, setQa] = useState<Qa>({ state: "loading" });
  const [attempt, setAttempt] = useState(0);
  const [issueCount, setIssueCount] = useState(0);
  const [tree, setTree] = useState<FileNode[] | null>(null);
  const [mock, setMock] = useState(false);
  const [options, setOptions] = useState<PublishOptions>(() => ({
    repo_name: defaultRepoName(detail.client_name, detail.title),
    private: true,
    open_issues: true,
    add_ci: true,
  }));
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  useEffect(() => {
    let live = true;
    api.runs
      .qaReport(runId)
      .then((a) => live && setQa({ state: "ready", report: a.data }))
      .catch((e: unknown) => live && setQa({ state: "error", message: e instanceof ApiError ? e.message : "Unknown error." }));
    return () => {
      live = false;
    };
  }, [runId, attempt]);

  // The issue count, file tree and mode only shape the confirm text, so a failure there is not an error state.
  useEffect(() => {
    let live = true;
    api.runs.requirements(runId).then((r) => live && setIssueCount(r.data.action_items.length)).catch(() => undefined);
    api.runs.files(runId).then((t) => live && setTree(t)).catch(() => undefined);
    api.health().then((h) => live && setMock(h.github_mode === "mock")).catch(() => undefined);
    return () => {
      live = false;
    };
  }, [runId]);

  const nameError = validateRepoName(options.repo_name);
  const report = qa.state === "ready" ? qa.report : null;
  const hasVideo = detail.artifacts.some((a) => a.type === "video");
  const fileCount = useMemo(() => estimateFileCount(tree, options, hasVideo), [tree, options, hasVideo]);
  const allowed = canPublish(report, nameError, busy);

  const confirm = useCallback(async () => {
    setBusy(true);
    setSubmitError(null);
    try {
      await api.runs.decidePublish(runId, options);
      setConfirming(false);
      notify.info("Publishing…", mock ? "Mock mode: nothing is sent to GitHub." : "Creating the repo and pushing the code.");
      onSubmitted();
    } catch (e) {
      setSubmitError(e instanceof Error ? e.message : "Something went wrong.");
    } finally {
      setBusy(false);
    }
  }, [runId, options, mock, onSubmitted]);

  return (
    <section className="screen" data-testid="gate2">
      <PageHead
        title="Ready to publish"
        description="Preview everything below. Nothing has left your machine."
        actions={
          <>
            {mock ? (
              <span className="mock-note" data-testid="mock-note">
                <TestTube aria-hidden="true" />
                Mock mode: nothing is sent to GitHub
              </span>
            ) : null}
            <ShareActions runId={runId} />
          </>
        }
      />
      <div className="grid-2">
        {qa.state === "loading" ? (
          <div className="panel">
            <div className="panel-body stack" aria-busy="true" aria-label="Loading the QA report">
              {[0, 1, 2].map((i) => (
                <span key={i} className="sk" style={{ width: `${95 - i * 15}%` }} />
              ))}
            </div>
          </div>
        ) : qa.state === "error" ? (
          <div className="banner err" role="alert">
            <CircleAlert className="icon" aria-hidden="true" />
            <div className="grow">
              <b>The QA report could not be loaded.</b>
              <p className="muted">{qa.message}</p>
              <div className="actions">
                <button type="button" className="btn sm" onClick={() => {
                    setQa({ state: "loading" });
                    setAttempt((n) => n + 1);
                  }}>
                  <RefreshCw className="icon" aria-hidden="true" />
                  Try again
                </button>
              </div>
            </div>
          </div>
        ) : (
          <QaReportPanel report={qa.report} />
        )}
        <div className="stack">
          <RepoPanel value={options} nameError={nameError} issueCount={issueCount} onChange={setOptions} />
          <RunStats detail={detail} />
        </div>
      </div>
      <PublishBar
        runId={runId}
        blocked={report?.block_publish ?? false}
        canPublish={allowed}
        busy={busy}
        onPublish={() => setConfirming(true)}
      />
      <ConfirmPublish
        open={confirming}
        options={options}
        fileCount={fileCount}
        issueCount={issueCount}
        mock={mock}
        busy={busy}
        error={submitError}
        onCancel={() => setConfirming(false)}
        onConfirm={() => void confirm()}
      />
    </section>
  );
}
