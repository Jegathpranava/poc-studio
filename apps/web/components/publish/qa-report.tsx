import { Check, CircleAlert, Info, X } from "lucide-react";

import type { QaReport } from "@/lib/api";
import { qaView } from "@/lib/publish";

const LABELS: Record<string, string> = {
  deck_present: "The deck was assembled",
  deck_self_contained: "The deck needs no network to open",
  spotlights_resolve: "Every deck spotlight finds its screen element",
  features_consistent: "The same features in the brief, prototype and deck",
  names_consistent: "The client name is spelled the same everywhere",
  costs_consistent: "The monthly cost matches in the architecture and the deck",
  figures_sourced: "Figures in the deck come from the brief",
  build_passed: "The prototype code builds",
  no_secrets: "No secrets in the generated files",
  no_pii: "No stray emails or phone numbers",
};

function label(name: string): string {
  return LABELS[name] ?? name.replace(/_/g, " ").replace(/^./, (c) => c.toUpperCase());
}

/** The QA report as a checklist: a tick or a cross per check, its detail, and the banners that matter. */
export function QaReportPanel({ report }: { report: QaReport }) {
  const view = qaView(report);
  const allPassed = view.passed === view.total;
  return (
    <div className="panel">
      <div className="panel-head">
        <h2>QA report</h2>
        <span className={`status ${allPassed ? "done" : "wait"}`}>
          {view.passed} of {view.total} checks passed
        </span>
      </div>
      <div className="panel-body">
        {view.blocked ? (
          <div className="banner err" role="alert" data-testid="blocked-banner">
            <CircleAlert className="icon" aria-hidden="true" />
            <div className="grow">
              <b>Publishing is blocked.</b>
              <p className="muted">A secret was found in the generated files. Nothing can be pushed until QA passes this check.</p>
            </div>
          </div>
        ) : null}
        {view.buildFailed ? (
          <div className="banner warn" role="note" data-testid="build-banner">
            <CircleAlert className="icon" aria-hidden="true" />
            <div className="grow">
              <b>Repo code did not build.</b>
              <p className="muted">
                You can still preview the deck and the prototype screens. Publishing the repo as it is will push code that fails
                its CI build.
              </p>
            </div>
          </div>
        ) : null}
        {view.deckMissing ? (
          <div className="banner warn" role="note" data-testid="deck-banner">
            <CircleAlert className="icon" aria-hidden="true" />
            <div className="grow">
              <b>The deck is missing.</b>
              <p className="muted">The pitch deck was not assembled, so the repo will have no deck/ folder.</p>
            </div>
          </div>
        ) : null}
        <ul className="list" aria-label="QA checks">
          {report.checks.map((c) => (
            <li key={c.name} className="qa-check" data-ok={c.ok}>
              {c.ok ? (
                <Check className="icon check" aria-label="Passed" />
              ) : (
                <X className="icon cross" aria-label="Failed" />
              )}
              <div className="grow">
                {label(c.name)}
                {!c.ok || c.detail !== "ok" ? <span className="detail">{c.detail}</span> : null}
              </div>
            </li>
          ))}
          {view.sentBack ? (
            <li>
              <Info className="icon" aria-hidden="true" />
              <div className="grow" data-testid="sent-back">
                {view.sentBack}
              </div>
            </li>
          ) : null}
        </ul>
      </div>
    </div>
  );
}
