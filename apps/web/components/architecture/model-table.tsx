import { usd, type ModelPick } from "@/lib/architecture";

export function ModelTable({ models }: { models: ModelPick[] }) {
  return (
    <div className="table-wrap">
      <table className="table cards">
        <thead>
          <tr>
            <th>Job</th>
            <th>Model</th>
            <th className="r">Per 1k calls</th>
          </tr>
        </thead>
        <tbody>
          {models.map((m) => (
            <tr key={`${m.job}-${m.model}`}>
              <td data-label="Job">{m.job}</td>
              <td className="mono small" data-label="Model">
                {m.model}
              </td>
              <td className="r mono num" data-label="Per 1k calls">
                {usd(m.cost_per_1k_calls_usd)}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
