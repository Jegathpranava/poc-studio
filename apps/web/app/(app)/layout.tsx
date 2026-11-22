import type { ReactNode } from "react";

import { AppShell } from "@/components/shell/app-shell";

// Every app route lives in this group, so it gets the rail and tab bar. `/share/[token]` sits outside it.
export default function AppLayout({ children }: { children: ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
