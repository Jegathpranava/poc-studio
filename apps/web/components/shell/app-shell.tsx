import { Suspense, type ReactNode } from "react";

import { Rail } from "./rail";
import { TabBar } from "./tab-bar";

// Rail and TabBar read the pathname on the client, which is only known at request time on dynamic routes.
export function AppShell({ children }: { children: ReactNode }) {
  return (
    <>
      <div className="shell">
        <Suspense fallback={<aside className="rail" aria-hidden="true" />}>
          <Rail />
        </Suspense>
        <main id="main">{children}</main>
      </div>
      <Suspense fallback={null}>
        <TabBar />
      </Suspense>
    </>
  );
}
