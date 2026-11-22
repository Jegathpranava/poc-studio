import { Check, Pause } from "lucide-react";
import Link from "next/link";

import type { GateView } from "@/lib/run-steps";

const COPY = {
  gate1: {
    passed: "Gate 1 approved by you",
    waiting: "Gate 1: you review the brief",
    idle: "Gate 1: you review the brief before anything is built",
    href: "brief",
    link: "View brief",
    open: "Review brief",
  },
  gate2: {
    passed: "Gate 2 approved by you",
    waiting: "Gate 2: you preview before anything is published",
    idle: "Gate 2: you preview before anything is published",
    href: "publish",
    link: "View preview",
    open: "Open preview",
  },
} as const;

export function GateRow({ gate, view, runId }: { gate: "gate1" | "gate2"; view: GateView; runId: string }) {
  const copy = COPY[gate];
  return (
    <div className={`gate${view === "passed" ? " passed" : ""}`} data-gate={gate} data-view={view}>
      <div className="gate-title">
        <span className="gnode">{view === "passed" ? <Check aria-hidden="true" /> : <Pause aria-hidden="true" />}</span>
        {copy[view]}
      </div>
      {view === "idle" ? (
        <span className="xs muted">Not reached yet</span>
      ) : (
        <Link href={`/runs/${runId}/${copy.href}`} className="small">
          {view === "passed" ? copy.link : copy.open}
        </Link>
      )}
    </div>
  );
}
