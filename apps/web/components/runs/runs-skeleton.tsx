const WIDTHS = ["62%", "48%", "70%", "40%", "56%"];

export function RunsSkeleton() {
  return (
    <div className="panel">
      <div className="panel-head">
        <span className="sk" style={{ width: 220, height: 30 }} />
      </div>
      <div className="panel-body stack" aria-busy="true" aria-label="Loading runs">
        {WIDTHS.map((w) => (
          <span className="sk" key={w} style={{ width: w }} />
        ))}
      </div>
    </div>
  );
}
