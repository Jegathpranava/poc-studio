"use client";

import type { PublishOptions } from "@/lib/api";
import { repoPath } from "@/lib/publish";

interface Props {
  value: PublishOptions;
  nameError: string | null;
  issueCount: number;
  disabled?: boolean;
  onChange: (next: PublishOptions) => void;
}

interface SwitchRow {
  key: "private" | "open_issues" | "add_ci";
  label: string;
  hint: string;
}

/** Repository settings: name with live validation, plus the private, issues and CI switches. */
export function RepoPanel({ value, nameError, issueCount, disabled = false, onChange }: Props) {
  const rows: SwitchRow[] = [
    { key: "private", label: "Private", hint: "Client work defaults to private" },
    {
      key: "open_issues",
      label: "Open issues from action items",
      hint: `${issueCount} ${issueCount === 1 ? "issue" : "issues"}`,
    },
    { key: "add_ci", label: "Add GitHub Actions CI", hint: "Install, then build" },
  ];
  return (
    <div className="panel">
      <div className="panel-head">
        <h2>Repository</h2>
      </div>
      <fieldset className="panel-body stack fieldset-plain" disabled={disabled}>
        <div className={`field${nameError ? " error" : ""}`}>
          <label htmlFor="repo-name">Name</label>
          <input
            id="repo-name"
            className="input mono"
            value={value.repo_name}
            spellCheck={false}
            autoComplete="off"
            aria-invalid={nameError !== null}
            aria-describedby="repo-name-hint"
            onChange={(e) => onChange({ ...value, repo_name: e.target.value.trim() })}
          />
          <span id="repo-name-hint" className="hint">
            {nameError ?? `github.com/${repoPath(value.repo_name)}`}
          </span>
        </div>
        {rows.map(({ key, label, hint }) => (
          <div key={key} className="switch">
            <div>
              <div className="small">
                <b>{label}</b>
              </div>
              <div className="xs muted">{hint}</div>
            </div>
            <button
              type="button"
              className="sw"
              role="switch"
              aria-checked={value[key]}
              aria-label={label}
              onClick={() => onChange({ ...value, [key]: !value[key] })}
            />
          </div>
        ))}
      </fieldset>
    </div>
  );
}
