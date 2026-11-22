"use client";

import { Pencil, Plus, Trash2 } from "lucide-react";
import { useState } from "react";

import { newFeature, type BriefForm } from "@/lib/brief-form";
import type { Feature, Priority } from "@/lib/requirements";

const PRIORITIES: Priority[] = ["P1", "P2", "P3"];

interface Props {
  features: Feature[];
  readOnly: boolean;
  onChange: (patch: Partial<BriefForm>) => void;
}

export function BriefFeatures({ features, readOnly, onChange }: Props) {
  const [editing, setEditing] = useState<number | null>(null);
  const set = (next: Feature[]) => onChange({ features: next });
  const patch = (i: number, p: Partial<Feature>) => set(features.map((f, j) => (j === i ? { ...f, ...p } : f)));

  return (
    <div className="panel">
      <div className="panel-head">
        <h2>Features, ranked</h2>
        {readOnly ? null : (
          <button
            type="button"
            className="btn sm"
            onClick={() => {
              set([...features, newFeature()]);
              setEditing(features.length);
            }}
          >
            <Plus className="icon" aria-hidden="true" />
            Add feature
          </button>
        )}
      </div>
      <div className="panel-body">
        <ul className="list">
          {features.map((f, i) =>
            editing === i && !readOnly ? (
              <li key={i}>
                <div className="feature-edit">
                  <input
                    className="input"
                    aria-label="Feature name"
                    value={f.name}
                    onChange={(e) => patch(i, { name: e.target.value })}
                  />
                  <textarea
                    className="textarea"
                    aria-label="Feature detail"
                    value={f.detail}
                    onChange={(e) => patch(i, { detail: e.target.value })}
                  />
                  <div className="chip-row">
                    <div className="seg" role="group" aria-label="Priority">
                      {PRIORITIES.map((p) => (
                        <button key={p} type="button" aria-pressed={f.priority === p} onClick={() => patch(i, { priority: p })}>
                          {p}
                        </button>
                      ))}
                    </div>
                    <button type="button" className="btn sm" onClick={() => setEditing(null)}>
                      Done
                    </button>
                    <button
                      type="button"
                      className="btn ghost sm"
                      aria-label="Remove feature"
                      onClick={() => {
                        set(features.filter((_, j) => j !== i));
                        setEditing(null);
                      }}
                    >
                      <Trash2 className="icon" aria-hidden="true" />
                    </button>
                  </div>
                </div>
              </li>
            ) : (
              <li key={i}>
                <span className="prio">{f.priority}</span>
                <div className="grow">
                  <b>{f.name || "Untitled feature"}</b>
                  {f.detail ? <div className="xs muted">{f.detail}</div> : null}
                </div>
                {readOnly ? null : (
                  <button type="button" className="btn ghost sm" aria-label={`Edit ${f.name || "feature"}`} onClick={() => setEditing(i)}>
                    <Pencil className="icon" aria-hidden="true" />
                  </button>
                )}
              </li>
            ),
          )}
        </ul>
      </div>
    </div>
  );
}
