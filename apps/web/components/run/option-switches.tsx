"use client";

export interface RunOptionsState {
  privateRepo: boolean;
  recordVideo: boolean;
  exportPptx: boolean;
  maskPii: boolean;
}

export const DEFAULT_OPTIONS: RunOptionsState = {
  privateRepo: true,
  recordVideo: true,
  exportPptx: false,
  maskPii: false,
};

const ROWS: { key: keyof RunOptionsState; label: string; hint: string }[] = [
  { key: "privateRepo", label: "Private client repo", hint: "Recommended for client work" },
  { key: "recordVideo", label: "Record a walkthrough video", hint: "Playwright, runs locally after Gate 2" },
  { key: "exportPptx", label: "Also export .pptx", hint: "The web deck is always made" },
  { key: "maskPii", label: "Mask names and emails", hint: "Before text reaches the models" },
];

interface Props {
  value: RunOptionsState;
  onChange: (next: RunOptionsState) => void;
  limitUsd: number;
}

export function OptionSwitches({ value, onChange, limitUsd }: Props) {
  return (
    <div className="panel">
      <div className="panel-head">
        <h2>Options</h2>
      </div>
      <div className="panel-body">
        {ROWS.map(({ key, label, hint }) => (
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
        <div className="switch">
          <div>
            <div className="small">
              <b>Paid spend limit for this run</b>
            </div>
            <div className="xs muted">The run pauses and asks if it is reached</div>
          </div>
          <span className="mono num small">${limitUsd.toFixed(2)}</span>
        </div>
      </div>
    </div>
  );
}
