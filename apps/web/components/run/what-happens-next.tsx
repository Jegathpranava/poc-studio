const STEPS = [
  { n: 1, body: "Brief and action items, then you review (Gate 1)" },
  { n: 2, body: "Architecture, prototype, deck and video, then QA" },
  { n: 3, body: "You preview everything before it is pushed (Gate 2)" },
];

export function WhatHappensNext() {
  return (
    <>
      <div className="small">
        <b>What happens next</b>
      </div>
      <ul className="list">
        {STEPS.map((s) => (
          <li key={s.n}>
            <span className="prio">{s.n}</span>
            <span className="grow">{s.body}</span>
          </li>
        ))}
      </ul>
    </>
  );
}
