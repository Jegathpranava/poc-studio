import type { RunStatus } from "@/lib/api";
import { statusLabel, statusTone } from "@/lib/run-labels";

export function StatusBadge({ status }: { status: RunStatus | null }) {
  if (!status) return <span className="badge wait">Connecting</span>;
  return (
    <span className={`badge ${statusTone(status)}`} role="status">
      {statusLabel(status)}
    </span>
  );
}
