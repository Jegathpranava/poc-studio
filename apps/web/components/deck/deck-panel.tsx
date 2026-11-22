import { ExternalLink } from "lucide-react";

import { api } from "@/lib/api";

/** The deck in a 16:9 frame. `sandbox` has no allow-same-origin, so the deck's scripts get an opaque origin. */
export function DeckPanel({ runId }: { runId: string }) {
  const src = api.runs.deckUrl(runId);
  return (
    <div className="panel deck-panel">
      <div className="panel-head">
        <h2>Interactive deck</h2>
        <div className="actions">
          <span className="xs muted mono">1280x720 stage, self-contained HTML</span>
          <a className="btn sm" href={src} target="_blank" rel="noopener">
            Open full screen
            <ExternalLink className="icon" aria-hidden="true" />
          </a>
        </div>
      </div>
      <div className="deck-frame">
        <iframe src={src} title="Interactive deck preview" sandbox="allow-scripts" loading="lazy" />
      </div>
      <div className="panel-body xs muted">Each slide steps through spotlights with captions. Arrow keys drive the deck.</div>
    </div>
  );
}
