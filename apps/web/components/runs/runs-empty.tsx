import { Inbox, Plus } from "lucide-react";
import Link from "next/link";

export function RunsEmpty() {
  return (
    <div className="panel">
      <div className="empty">
        <Inbox aria-hidden="true" />
        <h2>Start your first run</h2>
        <p>
          Drop in a meeting transcript, BRD or TRD. You get a brief, an architecture spec, a working prototype, a deck
          and a repo, with two checkpoints where you approve.
        </p>
        <div className="actions">
          <Link href="/runs/new" className="btn primary">
            <Plus className="icon" aria-hidden="true" />
            New run
          </Link>
        </div>
      </div>
    </div>
  );
}
