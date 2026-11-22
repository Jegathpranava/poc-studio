import type { BriefForm } from "@/lib/brief-form";

interface Props {
  form: BriefForm;
  onChange: (patch: Partial<BriefForm>) => void;
}

export function BriefGoalsPanel({ form, onChange }: Props) {
  const setConstraint = (i: number, patch: Partial<BriefForm["constraints"][number]>) =>
    onChange({ constraints: form.constraints.map((c, j) => (j === i ? { ...c, ...patch } : c)) });

  return (
    <div className="panel">
      <div className="panel-head">
        <h2>Goals and problem</h2>
        <span className="xs muted">from the transcript</span>
      </div>
      <div className="panel-body form-grid">
        <div className="field full">
          <label htmlFor="brief-title">Use case title</label>
          <input
            className="input"
            id="brief-title"
            value={form.title}
            maxLength={120}
            onChange={(e) => onChange({ title: e.target.value })}
          />
        </div>
        <div className="field full">
          <label htmlFor="brief-goals">Goals</label>
          <textarea
            className="textarea"
            id="brief-goals"
            value={form.goals}
            onChange={(e) => onChange({ goals: e.target.value })}
          />
          <span className="hint">One goal per line.</span>
        </div>
        <div className="field full">
          <label htmlFor="brief-pain">Pain points</label>
          <textarea
            className="textarea"
            id="brief-pain"
            value={form.painPoints}
            onChange={(e) => onChange({ painPoints: e.target.value })}
          />
          <span className="hint">One pain point per line.</span>
        </div>
        <div className="field">
          <label htmlFor="brief-budget">Budget</label>
          <input
            className="input"
            id="brief-budget"
            value={form.budgetText}
            onChange={(e) => onChange({ budgetText: e.target.value })}
          />
        </div>
        <div className="field">
          <label htmlFor="brief-amount">Budget amount in USD</label>
          <input
            className="input"
            id="brief-amount"
            inputMode="decimal"
            value={form.budgetAmount}
            onChange={(e) => onChange({ budgetAmount: e.target.value })}
          />
        </div>
        <div className="field full">
          <label htmlFor="brief-timeline">Timeline</label>
          <input
            className="input"
            id="brief-timeline"
            value={form.timeline}
            onChange={(e) => onChange({ timeline: e.target.value })}
          />
        </div>
        {form.constraints.map((c, i) => (
          <div key={i} className={`field full${c.confirmed ? "" : " error"}`}>
            <label htmlFor={`brief-constraint-${i}`}>Constraint {form.constraints.length > 1 ? i + 1 : ""}</label>
            <input
              className="input"
              id={`brief-constraint-${i}`}
              value={c.text}
              onChange={(e) => setConstraint(i, { text: e.target.value })}
            />
            {c.confirmed ? (
              c.source_quote ? <span className="hint">Said in the call: {c.source_quote}</span> : null
            ) : (
              <span className="hint">Not confirmed in the call. Check with the client or remove it.</span>
            )}
            <div className="actions">
              <button
                type="button"
                className="btn ghost sm"
                onClick={() => onChange({ constraints: form.constraints.filter((_, j) => j !== i) })}
              >
                Remove constraint
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
