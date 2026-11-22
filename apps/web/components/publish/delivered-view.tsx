import { Check, ChevronRight, Copy, ExternalLink, GitBranch, Link2, Monitor, Network, Presentation, Video } from "lucide-react";
import Link from "next/link";
import type { ReactNode } from "react";

import { PageHead } from "@/components/shell/page-head";
import type { PublishStatus, RunDetail } from "@/lib/api";
import { formatDuration, runTimes } from "@/lib/publish";

interface ItemProps {
  href: string;
  icon: ReactNode;
  title: string;
  sub: string;
}

function InAppItem({ href, icon, title, sub }: ItemProps) {
  return (
    <Link className="item" href={href}>
      {icon}
      <div className="grow">
        <b>{title}</b>
        <div className="u">{sub}</div>
      </div>
      <ChevronRight aria-hidden="true" />
    </Link>
  );
}

function summary(status: PublishStatus): string {
  const r = status.result;
  if (!r) return "The repo details are not available.";
  const issues = `${r.issues.length} ${r.issues.length === 1 ? "issue" : "issues"}`;
  return r.pushed
    ? `Repo pushed with ${r.file_count} files, ${issues} opened.`
    : `${r.file_count} files were committed locally and ${issues} planned. Nothing was sent to GitHub.`;
}

/** The Delivered state: a success banner and links to every deliverable. */
export function DeliveredView({ runId, detail, status }: { runId: string; detail: RunDetail; status: PublishStatus }) {
  const { agentMs } = runTimes(detail);
  const result = status.result;
  const hasVideo = detail.artifacts.some((a) => a.type === "video");
  const mock = status.mode === "mock";
  return (
    <section className="screen" data-testid="delivered">
      <PageHead
        title={agentMs === null ? "Delivered" : `Delivered in ${formatDuration(agentMs)}`}
        description={`Paid spend $${detail.paid_usd.toFixed(3)}. Send the share link to the client, or the pieces separately.`}
        actions={
          <button type="button" className="btn primary" disabled title="The client share page arrives in a later step">
            <Copy className="icon" aria-hidden="true" />
            Copy client share link
          </button>
        }
      />
      <div className="banner ok" role="status">
        <Check className="icon" aria-hidden="true" />
        <div className="grow">
          <b>{mock ? "Published in mock mode." : "Published."}</b> <span className="muted">{summary(status)}</span>
        </div>
      </div>
      <div className="deliver">
        {result ? (
          <a className="item" href={result.repo_url} target="_blank" rel="noopener noreferrer">
            <GitBranch className="lg" aria-hidden="true" />
            <div className="grow">
              <b>GitHub repo</b>
              <div className="u">{result.repo_url.replace("https://", "")}</div>
            </div>
            <ExternalLink aria-hidden="true" />
          </a>
        ) : null}
        <InAppItem
          href={`/runs/${runId}/prototype`}
          icon={<Monitor className="lg" aria-hidden="true" />}
          title="Prototype"
          sub="Live preview of the generated app"
        />
        <InAppItem
          href={`/runs/${runId}/deck`}
          icon={<Presentation className="lg" aria-hidden="true" />}
          title="Pitch deck"
          sub="Interactive deck, .pptx and docs"
        />
        {hasVideo ? (
          <InAppItem
            href={`/runs/${runId}/deck`}
            icon={<Video className="lg" aria-hidden="true" />}
            title="Walkthrough video"
            sub="MP4 with chapters"
          />
        ) : null}
        <InAppItem
          href={`/runs/${runId}/architecture`}
          icon={<Network className="lg" aria-hidden="true" />}
          title="Architecture spec"
          sub="Diagram, models and monthly cost"
        />
        <div className="item soon" aria-disabled="true">
          <Link2 className="lg" aria-hidden="true" />
          <div className="grow">
            <b>Client share page</b>
            <div className="u">Coming soon</div>
          </div>
        </div>
      </div>
    </section>
  );
}
