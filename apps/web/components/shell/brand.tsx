import { Terminal } from "lucide-react";

export function Brand() {
  return (
    <div className="brand">
      <span className="brand-mark">
        <Terminal aria-hidden="true" />
      </span>
      <span>PoC Studio</span>
    </div>
  );
}
