import { Check, Pause, RefreshCw } from "lucide-react";

interface Props {
  unconfirmed: number;
  busy: boolean;
  onReextract: () => void;
  onApprove: () => void;
}

/** Sticky Gate 1 decision bar. On a phone it sits above the tab bar. */
export function GateActionBar({ unconfirmed, busy, onReextract, onApprove }: Props) {
  return (
    <div className="action-bar" role="region" aria-label="Gate 1 decision">
      <div className="ab-text">
        <span className="gnode wait">
          <Pause aria-hidden="true" />
        </span>
        <div>
          <b>Gate 1: approve the brief</b>
          <div className="xs muted">
            {unconfirmed > 0
              ? `${unconfirmed} ${unconfirmed === 1 ? "field needs" : "fields need"} a check. `
              : ""}
            Nothing is designed or built until you approve.
          </div>
        </div>
      </div>
      <div className="actions">
        <button type="button" className="btn" onClick={onReextract} disabled={busy}>
          <RefreshCw className="icon" aria-hidden="true" />
          Re-extract with a note
        </button>
        <button type="button" className="btn primary" onClick={onApprove} disabled={busy}>
          <Check className="icon" aria-hidden="true" />
          Approve brief
        </button>
      </div>
    </div>
  );
}
