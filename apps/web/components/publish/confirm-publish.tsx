"use client";

import { GitBranch } from "lucide-react";
import { useEffect, useId } from "react";

import type { PublishOptions } from "@/lib/api";
import { repoPath } from "@/lib/publish";

interface Props {
  open: boolean;
  options: PublishOptions;
  fileCount: number | null;
  issueCount: number;
  mock: boolean;
  busy: boolean;
  error: string | null;
  onCancel: () => void;
  onConfirm: () => void;
}

/** The "Publish to GitHub?" confirmation, with the exact repo path and what will be pushed. */
export function ConfirmPublish({ open, options, fileCount, issueCount, mock, busy, error, onCancel, onConfirm }: Props) {
  const titleId = useId();
  useEffect(() => {
    if (!open) return;
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && !busy && onCancel();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, busy, onCancel]);
  if (!open) return null;

  const files = fileCount === null ? "the prototype files" : `about ${fileCount} files`;
  const issues = options.open_issues ? `opens ${issueCount} ${issueCount === 1 ? "issue" : "issues"} from the action items` : "opens no issues";
  return (
    <div className="scrim open" onMouseDown={(e) => e.target === e.currentTarget && !busy && onCancel()}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby={titleId}>
        <div className="panel-head">
          <h2 id={titleId}>Publish to GitHub?</h2>
        </div>
        <div className="panel-body">
          <p className="small" data-testid="confirm-summary">
            This creates <span className="mono">{repoPath(options.repo_name)}</span> as a{" "}
            <b>{options.private ? "private" : "public"}</b> repo, pushes {files}
            {options.add_ci ? " with a CI workflow" : ""} and {issues}.
          </p>
          <p className="small muted">
            Nothing has left your machine yet. {mock ? "Mock mode is on, so nothing will be sent to GitHub." : "You can delete the repo on GitHub afterwards."}
          </p>
          {error ? (
            <p className="hint bad" role="alert">
              {error}
            </p>
          ) : null}
        </div>
        <div className="modal-foot">
          <button type="button" className="btn" onClick={onCancel} disabled={busy}>
            Cancel
          </button>
          <button type="button" className="btn primary" onClick={onConfirm} disabled={busy}>
            <GitBranch className="icon" aria-hidden="true" />
            Publish
          </button>
        </div>
      </div>
    </div>
  );
}
