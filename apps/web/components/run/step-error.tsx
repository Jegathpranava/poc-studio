import { CircleAlert } from "lucide-react";

import type { EventError } from "@/lib/run-steps";

export function StepError({ error }: { error: EventError }) {
  const where = error.file ? `${error.file}${error.line ? `:${error.line}` : ""}${error.col ? `:${error.col}` : ""}` : null;
  return (
    <div className="errbox" role="alert">
      <div className="errbox-head">
        <CircleAlert className="icon" aria-hidden="true" />
        {where ? "Build error, stopped" : "This step stopped"}
      </div>
      {error.excerpt ? <pre className="code">{error.excerpt}</pre> : null}
      <div className="xs mono">
        {where ? `${where}  ` : ""}
        {error.message}
      </div>
    </div>
  );
}
