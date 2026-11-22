import type { Stat } from "./stats";

export function StatsStrip({ stats }: { stats: Stat[] }) {
  return (
    <div className="stats">
      {stats.map((s) => (
        <div className="stat" key={s.label}>
          <div className="k">{s.label}</div>
          <div className="v">{s.value}</div>
          {s.note ? <div className="xs muted">{s.note}</div> : null}
        </div>
      ))}
    </div>
  );
}
