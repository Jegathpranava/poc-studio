import { KeyRound } from "lucide-react";
import type { ReactNode } from "react";

/** Shows only whether a key is set, as "NAME is set in .env". The value never reaches the browser. */
export function KeyStatus({ name, isSet, children }: { name: string; isSet: boolean; children?: ReactNode }) {
  return (
    <div className="file-chip">
      <KeyRound className="icon" aria-hidden="true" />
      <div className="grow mono small" data-testid={`key-${name}`}>
        {name} {isSet ? "is set in .env" : "is not set in .env"}
      </div>
      {children}
    </div>
  );
}
