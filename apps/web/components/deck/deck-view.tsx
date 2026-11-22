"use client";

import { CircleAlert, Info } from "lucide-react";
import { useEffect, useState } from "react";

import { useRun } from "@/components/run/run-context";
import { PageHead } from "@/components/shell/page-head";
import { api, ApiError } from "@/lib/api";

import { DeckPanel } from "./deck-panel";
import { DocsPanel } from "./docs-panel";
import { VideoPanel, type VideoState } from "./video-panel";

const head = <PageHead title="Deck, video and docs" description="Interactive deck, walkthrough video and docs." />;

export function DeckView() {
  const { runId, status, detail, detailError } = useRun();
  const [video, setVideo] = useState<VideoState>({ state: "loading" });

  useEffect(() => {
    let live = true;
    api.runs
      .videoChapters(runId)
      .then((chapters) => live && setVideo({ state: "ready", chapters }))
      .catch((e: unknown) => {
        if (!live) return;
        if (e instanceof ApiError && e.status === 404) setVideo({ state: "missing" });
        else setVideo({ state: "error", message: e instanceof ApiError ? e.message : "Unknown error." });
      });
    return () => {
      live = false;
    };
  }, [runId, status]);

  const steps = detail?.steps ?? [];
  const last = [...steps].reverse().find((s) => s.agent === "video");
  const shown: VideoState =
    video.state === "missing" && last?.status === "failed"
      ? { state: "failed", message: last.error_message ?? "The recorder stopped with an error." }
      : video;
  const artifacts = detail?.artifacts ?? [];
  const hasDeck = artifacts.some((a) => a.type === "deck" && a.path.endsWith(".html"));

  if (detailError) {
    return (
      <section className="screen">
        {head}
        <div className="banner err" role="alert">
          <CircleAlert className="icon" aria-hidden="true" />
          <div className="grow">
            <b>The run could not be loaded.</b>
            <p className="muted">{detailError.message}</p>
          </div>
        </div>
      </section>
    );
  }
  if (!detail) {
    return (
      <section className="screen">
        {head}
        <div className="panel">
          <div className="panel-body" aria-busy="true" aria-label="Loading the deck">
            <span className="sk" style={{ width: "100%", height: 240 }} />
          </div>
        </div>
      </section>
    );
  }
  if (!hasDeck) {
    return (
      <section className="screen">
        {head}
        <div className="panel">
          <div className="empty">
            <Info aria-hidden="true" />
            <h2>Available after the deck is assembled</h2>
            <p>The deck, video and docs appear here once the prototype and pitch steps have finished.</p>
          </div>
        </div>
      </section>
    );
  }
  return (
    <section className="screen">
      {head}
      <DeckPanel runId={runId} />
      <div className="grid-2">
        <VideoPanel runId={runId} video={shown} />
        <DocsPanel runId={runId} artifacts={artifacts} />
      </div>
    </section>
  );
}
