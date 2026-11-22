/** Paid spend this month. No API for it yet, so it shows a placeholder until a later task wires it. */
export function BudgetMeter() {
  return (
    <div className="budget-meter">
      <div className="budget-row">
        <span>Paid spend this month</span>
        <span className="mono num">--</span>
      </div>
      <div className="bar" aria-hidden="true">
        <span style={{ width: "0%" }} />
      </div>
      <div style={{ marginTop: 6 }}>of $5.00 monthly cap</div>
    </div>
  );
}
