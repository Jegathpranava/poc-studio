import type { Metadata } from "next";
import type { ReactNode } from "react";

import "../share.css";

export const metadata: Metadata = { title: "Shared proof of concept", robots: { index: false, follow: false } };

/**
 * The client page has no app chrome. A clean split needs a route group with its own root layout, which
 * would move the files of other routes; until then the shell (rail, tab bar) is hidden by `share.css`
 * while this container is mounted, and nothing on the page links back into the app.
 */
export default function ShareLayout({ children }: { children: ReactNode }) {
  return <div className="share-root">{children}</div>;
}
