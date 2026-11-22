"use client";

import { useState } from "react";

import type { BriefForm } from "@/lib/brief-form";
import type { Requirements } from "@/lib/requirements";

interface Props {
  base: Requirements;
  form: BriefForm;
  onChange: (patch: Partial<BriefForm>) => void;
}

export function BriefSide({ base, form, onChange }: Props) {
  const [expanded, setExpanded] = useState(false);
  const toggle = (i: number, include: boolean) =>
    onChange({ actionItems: form.actionItems.map((a, j) => (j === i ? { ...a, include } : a)) });

  return (
    <div className="stack">
      <div className="panel">
        <div className="panel-head">
          <h2>Action items</h2>
          <span className="xs muted">become GitHub issues</span>
        </div>
        <div className="panel-body">
          {form.actionItems.length === 0 ? (
            <p className="small muted">No action items were found in the call.</p>
          ) : (
            <ul className="list">
              {form.actionItems.map(({ item, include }, i) => (
                <li key={i}>
                  <input
                    type="checkbox"
                    checked={include}
                    aria-label={`Include: ${item.text}`}
                    onChange={(e) => toggle(i, e.target.checked)}
                  />
                  <div className="grow">
                    {item.text}
                    <div className="xs muted">
                      {[item.owner ?? "No owner named", item.due].filter(Boolean).join(", ")}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      <div className="panel">
        <div className="panel-head">
          <h2>Stakeholders</h2>
        </div>
        <div className="panel-body">
          {base.stakeholders.length === 0 ? (
            <p className="small muted">No stakeholders were named.</p>
          ) : (
            <ul className="list">
              {base.stakeholders.map((s, i) => (
                <li key={i}>
                  <div className="grow">
                    <b>{s.name}</b>
                    <div className="xs muted">{s.role}</div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
      <div className="panel">
        <div className="panel-body">
          <div className="small">
            <b>Summary</b>
          </div>
          <p className={`small note-box${expanded ? "" : " clamp"}`} id="brief-summary">
            {base.summary}
          </p>
          <button type="button" className="more" aria-expanded={expanded} aria-controls="brief-summary" onClick={() => setExpanded((v) => !v)}>
            {expanded ? "Show less" : "Show more"}
          </button>
        </div>
      </div>
    </div>
  );
}
