"use client";

import { useParams } from "next/navigation";
import type { ReactNode } from "react";

import { RunProvider } from "./run-context";
import { RunSubnav } from "./run-subnav";

/** Wraps every page under /runs/[id]: one live connection per run (keyed, so another run starts with a clean timeline) and the sticky sub-nav. */
export function RunFrame({ children }: { children: ReactNode }) {
  const { id } = useParams<{ id: string }>();
  return (
    <RunProvider key={id} runId={id}>
      <RunSubnav />
      {children}
    </RunProvider>
  );
}
