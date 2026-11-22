import type { RunDetail } from "@/lib/api";
import { formatDuration, runTimes } from "@/lib/publish";

/** Agent time, paid spend and the time the owner spent at the gates. */
export function RunStats({ detail }: { detail: RunDetail }) {
  const { agentMs, gateMs } = runTimes(detail);
  return (
    <div className="panel">
      <div className="panel-body">
        <div className="small">
          <b>This run</b>
        </div>
        <ul className="list">
          <li>
            <span className="grow">Agent time</span>
            <span className="mono num small">{agentMs === null ? "--" : formatDuration(agentMs)}</span>
          </li>
          <li>
            <span className="grow">Paid spend</span>
            <span className="mono num small">
              ${detail.paid_usd.toFixed(3)} of ${detail.budget_usd.toFixed(2)}
            </span>
          </li>
          <li>
            <span className="grow">Your time at gates</span>
            <span className="mono num small">{gateMs === null ? "--" : formatDuration(gateMs)}</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
