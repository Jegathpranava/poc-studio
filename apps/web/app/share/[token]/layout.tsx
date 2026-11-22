import type { Metadata } from "next";
import type { ReactNode } from "react";

import "../share.css";

export const metadata: Metadata = { title: "Shared proof of concept", robots: { index: false, follow: false } };

/** The client page has no app chrome: it sits outside the `(app)` route group, so the shell never renders. */
export default function ShareLayout({ children }: { children: ReactNode }) {
  return <div className="share-root">{children}</div>;
}
