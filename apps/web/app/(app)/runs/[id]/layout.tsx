import { Suspense, type ReactNode } from "react";

import { RunFrame } from "@/components/run/run-frame";

// The run id is read on the client (useParams), so the layout itself stays static and prerenderable.
export default function RunLayout({ children }: { children: ReactNode }) {
  return (
    <Suspense fallback={<div className="subnav" aria-busy="true" />}>
      <RunFrame>{children}</RunFrame>
    </Suspense>
  );
}
