import type { ReactNode } from "react";

import { Rail } from "./rail";
import { TabBar } from "./tab-bar";

export function AppShell({ children }: { children: ReactNode }) {
  return (
    <>
      <div className="shell">
        <Rail />
        <main id="main">{children}</main>
      </div>
      <TabBar />
    </>
  );
}
