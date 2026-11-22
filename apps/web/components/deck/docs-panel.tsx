import { FileText, Presentation } from "lucide-react";

import { api, type RunDetail } from "@/lib/api";

export function DocsPanel({ runId, artifacts }: { runId: string; artifacts: RunDetail["artifacts"] }) {
  const has = (type: string, needle = "") => artifacts.some((a) => a.type === type && a.path.includes(needle));
  const rows = [
    { icon: Presentation, label: "Deck, self-contained HTML", note: "one file, works offline", action: "Download", href: api.runs.deckUrl(runId, true), ok: has("deck", ".html") },
    { icon: FileText, label: "Deck as .pptx", note: "static slides", action: "Download", href: api.runs.pptxUrl(runId), ok: has("pptx") },
    { icon: FileText, label: "Executive summary", note: "one page", action: "Open", href: api.runs.docUrl(runId, "exec-summary"), ok: has("docs", "exec-summary") },
    { icon: FileText, label: "User flows", note: "", action: "Open", href: api.runs.docUrl(runId, "user-flows"), ok: has("docs", "user-flows") },
  ];
  return (
    <div className="panel">
      <div className="panel-head">
        <h2>Docs and exports</h2>
      </div>
      <div className="panel-body">
        <ul className="list">
          {rows.map((r) => (
            <li key={r.label}>
              <r.icon className="icon" aria-hidden="true" />
              <span className="grow">
                {r.label} {r.note ? <span className="xs muted">{r.note}</span> : null}
              </span>
              {r.ok ? (
                <a href={r.href} className="small" target="_blank" rel="noopener">
                  {r.action}
                </a>
              ) : (
                <span className="small muted">Not ready</span>
              )}
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
