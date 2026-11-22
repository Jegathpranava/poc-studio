import Link from "next/link";
import type { ReactNode } from "react";

import type { RunStatus } from "@/lib/api";

export function NextForYou({ status, runId }: { status: RunStatus | null; runId: string }) {
  let body: ReactNode;
  switch (status) {
    case "waiting_gate1":
      body = (
        <>
          The brief is ready. Nothing is designed or built until you approve it.{" "}
          <Link href={`/runs/${runId}/brief`}>Review the brief</Link>.
        </>
      );
      break;
    case "waiting_gate2":
      body = "The prototype and deck are ready to preview before anything is published.";
      break;
    case "paused_budget":
      body = "The run reached its paid spend limit and is waiting for you to raise it.";
      break;
    case "failed":
      body = "A step stopped. The brief and anything finished before it are saved.";
      break;
    case "delivered":
      body = "This run is delivered.";
      break;
    default:
      body = "Agents are working. This page updates by itself; you can leave it open.";
  }
  return (
    <div className="panel">
      <div className="panel-body small">
        <b>Next for you</b>
        <p className="note-box">{body}</p>
      </div>
    </div>
  );
}
