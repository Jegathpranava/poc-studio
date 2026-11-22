import { Search } from "lucide-react";

import type { RunSummary } from "@/lib/api";

import { RunRow } from "./run-row";

export function RunsTable({ runs, query }: { runs: RunSummary[]; query: string }) {
  if (runs.length === 0) {
    return (
      <div className="empty">
        <Search aria-hidden="true" />
        <h3>{query.trim() ? `No runs match "${query.trim()}"` : "No runs in this view"}</h3>
        <p>Try a client name or a sector such as fintech.</p>
      </div>
    );
  }
  return (
    <table className="table responsive">
      <thead>
        <tr>
          <th>Client and use case</th>
          <th>Sector</th>
          <th>Status</th>
          <th>Agent time</th>
          <th className="r">Paid spend</th>
          <th>Started</th>
        </tr>
      </thead>
      <tbody>
        {runs.map((r) => (
          <RunRow key={r.id} run={r} />
        ))}
      </tbody>
    </table>
  );
}
