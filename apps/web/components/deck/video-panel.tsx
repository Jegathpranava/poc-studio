"use client";

import { CircleAlert, Download, Info } from "lucide-react";
import { useRef, useState } from "react";

import { api, type Chapter } from "@/lib/api";

export type VideoState =
  | { state: "loading" }
  | { state: "missing" }
  | { state: "failed"; message: string }
  | { state: "error"; message: string }
  | { state: "ready"; chapters: Chapter[] };

export const formatTime = (t: number) => {
  const s = Math.max(0, Math.round(t));
  return `${Math.floor(s / 60)}:${String(s % 60).padStart(2, "0")}`;
};

function ErrorBanner({ title, message }: { title: string; message: string }) {
  return (
    <div className="banner err" role="alert">
      <CircleAlert className="icon" aria-hidden="true" />
      <div className="grow">
        <b>{title}</b>
        <p className="muted">{message}</p>
      </div>
    </div>
  );
}

export function VideoPanel({ runId, video }: { runId: string; video: VideoState }) {
  const ref = useRef<HTMLVideoElement>(null);
  const [broken, setBroken] = useState(false);
  const src = api.runs.videoUrl(runId);

  const seek = (t: number) => {
    const el = ref.current;
    if (!el) return;
    el.currentTime = t;
    void el.play?.()?.catch?.(() => undefined);
  };

  return (
    <div className="panel">
      <div className="panel-head">
        <h2>Walkthrough video</h2>
        <span className="xs muted mono">MP4, 1280x720</span>
      </div>
      <div className="panel-body stack">
        {video.state === "loading" ? (
          <div aria-busy="true" aria-label="Loading the video">
            <span className="sk" style={{ width: "100%", height: 200 }} />
          </div>
        ) : null}
        {video.state === "missing" ? (
          <div className="empty">
            <Info aria-hidden="true" />
            <h3>No video yet</h3>
            <p>The video is recorded after you approve Gate 2.</p>
          </div>
        ) : null}
        {video.state === "failed" ? <ErrorBanner title="The video could not be recorded." message={video.message} /> : null}
        {video.state === "error" ? <ErrorBanner title="The video could not be loaded." message={video.message} /> : null}
        {video.state === "ready" ? (
          <>
            <video ref={ref} className="player" controls preload="metadata" playsInline src={src} onError={() => setBroken(true)}>
              Your browser cannot play MP4 here.
            </video>
            {broken ? <ErrorBanner title="The video file is missing." message="Re-run the video step." /> : null}
            <ul className="chapters" aria-label="Chapters">
              {video.chapters.map((c, i) => (
                <li key={`${i}-${c.t}`}>
                  <button type="button" className="chapter-btn" onClick={() => seek(c.t)}>
                    <span className="t">{formatTime(c.t)}</span>
                    {c.title}
                  </button>
                </li>
              ))}
            </ul>
            <div className="actions">
              <a className="btn sm" href={src} download>
                <Download className="icon" aria-hidden="true" />
                Download MP4
              </a>
            </div>
          </>
        ) : null}
      </div>
    </div>
  );
}
