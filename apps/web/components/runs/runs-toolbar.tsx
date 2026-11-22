import { Search } from "lucide-react";

import type { StatusFilter } from "./format";

const FILTERS: { value: StatusFilter; label: string }[] = [
  { value: "all", label: "All" },
  { value: "wait", label: "Waiting for you" },
  { value: "done", label: "Delivered" },
];

interface RunsToolbarProps {
  query: string;
  onQuery: (q: string) => void;
  filter: StatusFilter;
  onFilter: (f: StatusFilter) => void;
}

export function RunsToolbar({ query, onQuery, filter, onFilter }: RunsToolbarProps) {
  return (
    <div className="panel-head">
      <div className="toolbar">
        <label className="search">
          <Search className="icon" aria-hidden="true" />
          <input
            value={query}
            onChange={(e) => onQuery(e.target.value)}
            placeholder="Search client or sector"
            aria-label="Search runs"
          />
        </label>
        <div className="seg" role="group" aria-label="Status filter">
          {FILTERS.map((f) => (
            <button key={f.value} type="button" aria-pressed={filter === f.value} onClick={() => onFilter(f.value)}>
              {f.label}
            </button>
          ))}
        </div>
      </div>
      <span className="xs muted">Click a run to open it</span>
    </div>
  );
}
