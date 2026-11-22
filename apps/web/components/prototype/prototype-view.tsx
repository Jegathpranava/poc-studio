"use client";

import { CircleAlert, ExternalLink, Info, MessageSquare, RefreshCw } from "lucide-react";
import { useEffect, useState } from "react";

import { useRun } from "@/components/run/run-context";
import { notify } from "@/components/shell/notify";
import { PageHead } from "@/components/shell/page-head";
import { api, ApiError, type BuildInfo, type FileNode } from "@/lib/api";

import { BuildLog, BuildStatus } from "./build-log";
import { DeviceFrame, DeviceToggle, type Device } from "./device-frame";
import { FileTree } from "./file-tree";

/** Re-asking for the preview counts as activity, so the API's 30-minute idle reaper leaves it alone. */
const HEARTBEAT_MS = 5 * 60 * 1000;

type Build =
  | { state: "loading" }
  | { state: "none" } // 404 or 409: the Prototype Builder has not produced a build yet
  | { state: "error"; error: ApiError }
  | { state: "ready"; info: BuildInfo };

type Preview =
  | { state: "idle" }
  | { state: "starting" }
  | { state: "failed"; message: string }
  | { state: "ready"; url: string };

const notBuilt = (e: unknown) => e instanceof ApiError && (e.status === 404 || e.status === 409);

export function PrototypeView() {
  const { runId, status } = useRun();
  const [build, setBuild] = useState<Build>({ state: "loading" });
  const [files, setFiles] = useState<FileNode[]>([]);
  const [preview, setPreview] = useState<Preview>({ state: "idle" });
  const [device, setDevice] = useState<Device>("desktop");
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let live = true;
    api.runs
      .build(runId)
      .then((info) => live && setBuild({ state: "ready", info }))
      .catch((e: unknown) => {
        if (!live) return;
        if (notBuilt(e)) setBuild((b) => (b.state === "ready" ? b : { state: "none" }));
        else setBuild({ state: "error", error: e instanceof ApiError ? e : new ApiError("Unknown error.") });
      });
    api.runs
      .files(runId)
      .then((tree) => live && setFiles(tree))
      .catch(() => live && setFiles([]));
    return () => {
      live = false;
    };
  }, [runId, status]);

  const built = build.state === "ready" && build.info.ok;
  useEffect(() => {
    if (!built) return;
    let live = true;
    const start = (first: boolean) => {
      if (first) setPreview({ state: "starting" });
      api.runs
        .startPreview(runId)
        .then((p) => live && setPreview({ state: "ready", url: p.url }))
        .catch((e: unknown) => {
          if (live && first) setPreview({ state: "failed", message: e instanceof ApiError ? e.message : "Unknown error." });
        });
    };
    start(true);
    const timer = window.setInterval(() => start(false), HEARTBEAT_MS);
    return () => {
      live = false;
      window.clearInterval(timer);
    };
  }, [runId, built, attempt]);

  const url = preview.state === "ready" ? preview.url : null;
  const actions = (
    <>
      <button type="button" className="btn" onClick={() => notify.info("Request changes arrives in a later step")}>
        <MessageSquare className="icon" aria-hidden="true" />
        Request changes
      </button>
      {url ? (
        <a className="btn" href={url} target="_blank" rel="noopener">
          Open in new tab
          <ExternalLink className="icon" aria-hidden="true" />
        </a>
      ) : (
        <button type="button" className="btn" disabled title="The preview is not running yet">
          Open in new tab
          <ExternalLink className="icon" aria-hidden="true" />
        </button>
      )}
    </>
  );
  const head = <PageHead title="Prototype" actions={actions} />;

  if (build.state === "loading") {
    return (
      <section className="screen">
        {head}
        <div className="panel">
          <div className="panel-body stack" aria-busy="true" aria-label="Loading the prototype">
            {[0, 1, 2].map((i) => (
              <span key={i} className="sk" style={{ width: `${95 - i * 15}%` }} />
            ))}
          </div>
        </div>
      </section>
    );
  }

  if (build.state === "error") {
    return (
      <section className="screen">
        {head}
        <div className="banner err" role="alert">
          <CircleAlert className="icon" aria-hidden="true" />
          <div className="grow">
            <b>The prototype could not be loaded.</b>
            <p className="muted">{build.error.message}</p>
            <div className="actions">
              <button type="button" className="btn sm" onClick={() => window.location.reload()}>
                <RefreshCw className="icon" aria-hidden="true" />
                Try again
              </button>
            </div>
          </div>
        </div>
      </section>
    );
  }

  if (build.state === "none") {
    return (
      <section className="screen">
        {head}
        <div className="panel">
          <div className="empty">
            <Info aria-hidden="true" />
            <h2>Available after the Prototype Builder runs</h2>
            <p>The prototype appears here once the brief is approved and the app has been built.</p>
          </div>
        </div>
      </section>
    );
  }

  const info = build.info;
  return (
    <section className="screen">
      {head}
      <div className="grid-2">
        <div className="panel">
          <div className="panel-head">
            <DeviceToggle value={device} onChange={setDevice} />
            <span className="xs muted mono">{url ? url.replace(/^https?:\/\//, "").replace(/\/$/, "") : ""}</span>
          </div>
          {info.ok ? (
            <PreviewPane preview={preview} device={device} onRetry={() => setAttempt((n) => n + 1)} />
          ) : (
            <div className="panel-body">
              <div className="banner err" role="alert">
                <CircleAlert className="icon" aria-hidden="true" />
                <div className="grow">
                  <b>The build failed, so there is no preview.</b>
                  <p className="muted">Retry arrives in a later step.</p>
                </div>
              </div>
            </div>
          )}
        </div>
        <div className="stack">
          <div className="panel">
            <div className="panel-head">
              <h2>Files</h2>
              <span className="xs muted">read only</span>
            </div>
            <FileTree nodes={files} />
          </div>
          <div className="panel">
            <div className="panel-head">
              <h2>Build log</h2>
              <BuildStatus build={info} />
            </div>
            <BuildLog build={info} />
          </div>
        </div>
      </div>
    </section>
  );
}

function PreviewPane({ preview, device, onRetry }: { preview: Preview; device: Device; onRetry: () => void }) {
  if (preview.state === "failed") {
    return (
      <div className="panel-body">
        <div className="banner err" role="alert">
          <CircleAlert className="icon" aria-hidden="true" />
          <div className="grow">
            <b>The preview could not start.</b>
            <p className="muted">{preview.message}</p>
            <div className="actions">
              <button type="button" className="btn sm" onClick={onRetry}>
                <RefreshCw className="icon" aria-hidden="true" />
                Try again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }
  if (preview.state !== "ready") {
    return (
      <div className="panel-body" aria-busy="true">
        <p className="small muted">Starting the preview…</p>
        <span className="sk" style={{ width: "80%" }} />
      </div>
    );
  }
  return (
    <DeviceFrame device={device} url={preview.url}>
      <iframe className="proto-frame" title="Prototype preview" src={preview.url} />
    </DeviceFrame>
  );
}
