import { GitBranch, Monitor, Pause, Presentation } from "lucide-react";
import Link from "next/link";

interface Props {
  runId: string;
  blocked: boolean;
  canPublish: boolean;
  busy: boolean;
  onPublish: () => void;
}

/** Sticky Gate 2 bar. Preview links go to the run's own pages; Publish opens the confirm modal. */
export function PublishBar({ runId, blocked, canPublish, busy, onPublish }: Props) {
  return (
    <div className="action-bar" role="region" aria-label="Gate 2 decision">
      <div className="ab-text">
        <span className="gnode wait">
          <Pause aria-hidden="true" />
        </span>
        <div>
          <b>Gate 2: publish</b>
          <div className="xs muted">
            {blocked ? "Publishing is blocked by QA." : "Nothing has left your machine yet."}
          </div>
        </div>
      </div>
      <div className="actions">
        <Link className="btn" href={`/runs/${runId}/prototype`}>
          <Monitor className="icon" aria-hidden="true" />
          Preview prototype
        </Link>
        <Link className="btn" href={`/runs/${runId}/deck`}>
          <Presentation className="icon" aria-hidden="true" />
          Preview deck
        </Link>
        <button type="button" className="btn primary" onClick={onPublish} disabled={!canPublish || busy}>
          <GitBranch className="icon" aria-hidden="true" />
          Publish to GitHub
        </button>
      </div>
    </div>
  );
}
