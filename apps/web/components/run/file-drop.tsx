"use client";

import { File as FileIcon, Trash2, Upload } from "lucide-react";
import { useRef, useState, type DragEvent } from "react";

import { ACCEPTED_EXTENSIONS, checkFiles, formatBytes, type Rejection } from "@/lib/upload";

interface Props {
  files: File[];
  onChange: (files: File[]) => void;
  /** Shown as an error when the form was submitted without files. */
  error?: string | null;
}

/** Drop zone and chip list. Files that fail the type or size check are refused with a message. */
export function FileDrop({ files, onChange, error }: Props) {
  const input = useRef<HTMLInputElement>(null);
  const [over, setOver] = useState(false);
  const [rejected, setRejected] = useState<Rejection[]>([]);

  const add = (incoming: File[]) => {
    const { accepted, rejected: bad } = checkFiles(incoming, files);
    setRejected(bad);
    if (accepted.length > 0) onChange([...files, ...accepted]);
  };

  const onDrop = (e: DragEvent) => {
    e.preventDefault();
    setOver(false);
    add([...e.dataTransfer.files]);
  };

  return (
    <div className="stack">
      <div
        className={`drop${over ? " over" : ""}`}
        onDragOver={(e) => {
          e.preventDefault();
          setOver(true);
        }}
        onDragLeave={() => setOver(false)}
        onDrop={onDrop}
      >
        <Upload className="icon-lg" aria-hidden="true" />
        <b>Drop a transcript or requirements doc</b>
        <span className="small muted">
          {ACCEPTED_EXTENSIONS.join(", ")}, up to 20 MB each. Several files become one brief.
        </span>
        <input
          ref={input}
          type="file"
          multiple
          accept={ACCEPTED_EXTENSIONS.join(",")}
          aria-label="Choose files"
          data-testid="file-input"
          onChange={(e) => {
            add([...(e.target.files ?? [])]);
            e.target.value = "";
          }}
        />
        <button type="button" className="btn sm" onClick={() => input.current?.click()}>
          Choose files
        </button>
      </div>
      {rejected.length > 0 ? (
        <div className="banner err" role="alert">
          <div className="grow">
            {rejected.map((r) => (
              <div key={r.name}>
                <b>{r.name}</b> {r.reason}
              </div>
            ))}
          </div>
        </div>
      ) : null}
      {error ? (
        <p className="hint bad" role="alert">
          {error}
        </p>
      ) : null}
      {files.map((f) => (
        <div key={`${f.name}:${f.size}`} className="file-chip">
          <FileIcon className="icon" aria-hidden="true" />
          <div className="grow">
            <div className="name">{f.name}</div>
            <div className="xs muted">{formatBytes(f.size)}</div>
          </div>
          <button
            type="button"
            className="btn ghost sm"
            aria-label={`Remove ${f.name}`}
            onClick={() => onChange(files.filter((x) => x !== f))}
          >
            <Trash2 className="icon" aria-hidden="true" />
          </button>
        </div>
      ))}
    </div>
  );
}
