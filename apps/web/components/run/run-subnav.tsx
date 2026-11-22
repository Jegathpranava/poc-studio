"use client";

import { ChevronRight } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

import { StatusBadge } from "./status-badge";
import { useRun } from "./run-context";

const TABS: { slug: string; label: string }[] = [
  { slug: "", label: "Timeline" },
  { slug: "brief", label: "Brief" },
  { slug: "architecture", label: "Architecture" },
  { slug: "prototype", label: "Prototype" },
  { slug: "deck", label: "Deck and video" },
  { slug: "publish", label: "Publish" },
];

export function RunSubnav() {
  const { runId, detail, status } = useRun();
  const pathname = usePathname();
  const base = `/runs/${runId}`;
  const current = pathname.slice(base.length).replace(/^\//, "").split("/")[0] ?? "";

  return (
    <div className="subnav">
      <div className="subnav-id">
        <Link href="/">Runs</Link>
        <ChevronRight className="icon sep" aria-hidden="true" />
        <b>{detail?.client_name ?? "Loading"}</b>
        <span className="rid" title="Run ID">
          {runId}
        </span>
        {detail?.sector ? <span className="tag">{detail.sector}</span> : null}
        <StatusBadge status={status} />
      </div>
      <nav className="subnav-tabs" aria-label="Run pages">
        {TABS.map(({ slug, label }) => (
          <Link
            key={label}
            href={slug ? `${base}/${slug}` : base}
            aria-current={slug === current ? "page" : undefined}
          >
            {label}
          </Link>
        ))}
      </nav>
    </div>
  );
}
