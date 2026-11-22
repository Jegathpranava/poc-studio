import { usd, type MonthlyCost } from "@/lib/architecture";

export function CostTable({ cost }: { cost: MonthlyCost }) {
  return (
    <div className="table-wrap">
      <table className="table cards">
        <tbody>
          {cost.lines.map((line) => (
            <tr key={line.item}>
              <td data-label="Item">{line.item}</td>
              <td className="r mono num" data-label="USD / month">
                {usd(line.usd)}
              </td>
            </tr>
          ))}
          <tr>
            <td data-label="Item">
              <b>Total</b>
            </td>
            <td className="r mono num" data-label="USD / month">
              <b>{usd(cost.total_usd)}</b>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
