import { formatCost, formatTokens, modelLabel } from "@/lib/run-labels";
import { costByModel, type TimelineState } from "@/lib/run-steps";

export function CostByModel({ state }: { state: TimelineState }) {
  const rows = costByModel(state);
  return (
    <div className="panel">
      <div className="panel-head">
        <h2>Cost by model</h2>
      </div>
      {rows.length === 0 ? (
        <div className="panel-body small muted">No model has been called yet.</div>
      ) : (
        <div className="table-wrap">
          <table className="table cards">
            <thead>
              <tr>
                <th>Model</th>
                <th className="r">Tokens</th>
                <th className="r">Cost</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.model}>
                  <td data-label="Model">{modelLabel(r.model)}</td>
                  <td className="r mono num" data-label="Tokens">
                    {formatTokens(r.tokens)}
                  </td>
                  <td className="r mono num" data-label="Cost">
                    {formatCost(r.costUsd)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
