"use client";

import { AlertCircle, ExternalLink, Presentation } from "lucide-react";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";

import { ApiError } from "@/lib/api";
import { formatExpiry, shareApi, type SharePage } from "@/lib/share-api";

type State = { kind: "loading" } | { kind: "invalid" } | { kind: "error"; message: string } | { kind: "ok"; page: SharePage };

/** The client-facing page behind a token. It links nowhere inside the app (no runs, settings or templates). */
export function ShareView({ token }: { token: string }) {
  const [state, setState] = useState<State>({ kind: "loading" });

  useEffect(() => {
    let live = true;
    shareApi
      .page(token)
      .then((page) => live && setState({ kind: "ok", page }))
      .catch((e: unknown) => {
        if (!live) return;
        if (e instanceof ApiError && e.status === 404) setState({ kind: "invalid" });
        else setState({ kind: "error", message: e instanceof Error ? e.message : "Something went wrong." });
      });
    return () => {
      live = false;
    };
  }, [token]);

  if (state.kind === "loading") {
    return (
      <div className="share" aria-busy="true" aria-label="Loading">
        <span className="sk" style={{ width: "40%" }} />
        <span className="sk" style={{ width: "70%", height: 24, marginTop: 12 }} />
        <span className="sk" style={{ width: "100%", height: 220, marginTop: 24 }} />
      </div>
    );
  }
  if (state.kind !== "ok") {
    return (
      <div className="share">
        <div className="empty" role="alert">
          <AlertCircle aria-hidden="true" />
          <h1>{state.kind === "invalid" ? "This link has expired or is not valid" : "This page could not be loaded"}</h1>
          <p>
            {state.kind === "invalid"
              ? "Ask the person who sent it for a new link or a fresh zip."
              : state.message}
          </p>
        </div>
      </div>
    );
  }
  const { page } = state;
  return (
    <div className="share">
      <header>
        <div className="xs muted">Prepared for {page.client} by Skyform</div>
        <h1>{page.title}</h1>
        <p className="muted share-summary">{page.summary}</p>
      </header>
      <div className="stack">
        {page.video_url ? (
          <video className="player" controls preload="metadata" playsInline src={shareApi.asset(page.video_url)}>
            Your browser cannot play MP4 here.
          </video>
        ) : null}
        {page.deck_url ? (
          <div className="deliver">
            <a className="item" href={shareApi.asset(page.deck_url)} target="_blank" rel="noopener noreferrer">
              <Presentation className="lg" aria-hidden="true" />
              <div className="grow">
                <b>Open the interactive deck</b>
                <div className="u">Click through each screen, step by step</div>
              </div>
              <ExternalLink aria-hidden="true" />
            </a>
          </div>
        ) : null}
        {page.pain_points.length > 0 ? (
          <div className="panel">
            <div className="panel-body">
              <h2>What we heard</h2>
              <ul className="list">
                {page.pain_points.map((p) => (
                  <li key={p}>
                    <span className="grow">{p}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        ) : null}
        {page.pilot ? <p className="xs muted">{page.pilot}</p> : null}
      </div>
      <footer className="share-foot">
        Shared by Skyform. This page is read-only and expires on {formatExpiry(page.expires_at)}.
      </footer>
    </div>
  );
}

/** The route entry: the token comes from the URL on the client, like the run pages read their id. */
export function ShareRoute() {
  const { token } = useParams<{ token: string }>();
  return <ShareView token={token} />;
}
