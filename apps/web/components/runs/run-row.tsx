"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import type { RunSummary } from "@/lib/api";

import { PLACEHOLDER, durationMs, formatDuration, formatUsd, formatWhen, statusView } from "./format";

export function RunRow({ run }: { run: RunSummary }) {
  const router = useRouter();
  const href = `/runs/${run.id}`;
  const { tone, label } = statusView(run);
  return (
    <tr onClick={() => router.push(href)}>
      <td>
        <Link className="client" href={href} onClick={(e) => e.stopPropagation()}>
          {run.client_name}
        </Link>
        <div className="xs muted">{run.title}</div>
      </td>
      <td className="hide-sm">{run.sector ? <span className="tag">{run.sector}</span> : PLACEHOLDER}</td>
      <td>
        <span className={`status ${tone}`}>{label}</span>
      </td>
      <td className="hide-sm mono num small">{formatDuration(durationMs(run))}</td>
      <td className="r mono num small">{formatUsd(run.paid_usd)}</td>
      <td className="hide-sm muted small">{formatWhen(run.started_at)}</td>
    </tr>
  );
}
