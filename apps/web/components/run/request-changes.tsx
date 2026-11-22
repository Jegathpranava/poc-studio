"use client";

import { useEffect, useId, useRef, useState } from "react";

interface RequestChangesProps {
  open: boolean;
  title: string;
  description?: string;
  placeholder?: string;
  sendLabel?: string;
  busy?: boolean;
  error?: string | null;
  onCancel: () => void;
  /** Receives the note. The caller decides what to do with it (Task 19 wires the revise endpoints). */
  onSend: (note: string) => void;
}

/** A small modal with a note field, Cancel and Send. It holds no API logic. */
export function RequestChanges({
  open,
  title,
  description,
  placeholder = "Say what to change",
  sendLabel = "Send",
  busy = false,
  error = null,
  onCancel,
  onSend,
}: RequestChangesProps) {
  const [note, setNote] = useState("");
  const area = useRef<HTMLTextAreaElement>(null);
  const titleId = useId();

  useEffect(() => {
    if (!open) return;
    area.current?.focus();
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && !busy && onCancel();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [open, busy, onCancel]);

  if (!open) return null;
  const empty = note.trim().length === 0;

  return (
    <div className="scrim open" onMouseDown={(e) => e.target === e.currentTarget && !busy && onCancel()}>
      <div className="modal" role="dialog" aria-modal="true" aria-labelledby={titleId}>
        <div className="panel-head">
          <h2 id={titleId}>{title}</h2>
        </div>
        <div className="panel-body">
          {description ? <p className="small muted">{description}</p> : null}
          <div className="field">
            <label htmlFor={`${titleId}-note`}>Note</label>
            <textarea
              id={`${titleId}-note`}
              ref={area}
              className="textarea"
              value={note}
              placeholder={placeholder}
              onChange={(e) => setNote(e.target.value)}
            />
            {error ? <span className="hint bad">{error}</span> : null}
          </div>
        </div>
        <div className="modal-foot">
          <button type="button" className="btn" onClick={onCancel} disabled={busy}>
            Cancel
          </button>
          <button type="button" className="btn primary" onClick={() => onSend(note.trim())} disabled={empty || busy}>
            {sendLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
