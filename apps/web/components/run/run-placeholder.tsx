import { Clock } from "lucide-react";

import { PageHead } from "@/components/shell/page-head";

export function RunPlaceholder({ title, after }: { title: string; after: string }) {
  return (
    <section className="screen">
      <PageHead title={title} />
      <div className="panel">
        <div className="empty">
          <Clock aria-hidden="true" />
          <h2>Available after {after}</h2>
          <p>This page fills in as the run reaches that step.</p>
        </div>
      </div>
    </section>
  );
}
