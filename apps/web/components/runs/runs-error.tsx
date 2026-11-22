import { CircleAlert, RefreshCw } from "lucide-react";

export function RunsError({ onRetry }: { onRetry: () => void }) {
  return (
    <div className="banner err" role="alert">
      <CircleAlert className="icon" aria-hidden="true" />
      <div className="grow">
        <b>The PoC Studio API is not answering on port 8000.</b>
        <p className="muted">
          Start it with <span className="mono">npm run dev</span> from the project folder, then try again.
        </p>
        <div className="actions">
          <button type="button" className="btn sm" onClick={onRetry}>
            <RefreshCw className="icon" aria-hidden="true" />
            Try again
          </button>
        </div>
      </div>
    </div>
  );
}
