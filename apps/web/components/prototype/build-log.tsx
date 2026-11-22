import type { BuildInfo } from "@/lib/api";
import { StepError } from "@/components/run/step-error";

export function BuildStatus({ build }: { build: BuildInfo }) {
  const attempts = build.attempts ?? 1;
  return build.ok ? (
    <span className="status done">Build passed{attempts > 1 ? ` on attempt ${attempts}` : ""}</span>
  ) : (
    <span className="status fail">Build failed after {attempts} {attempts === 1 ? "attempt" : "attempts"}</span>
  );
}

/** The build outcome, the structured error when it failed, and the tail of the log. */
export function BuildLog({ build }: { build: BuildInfo }) {
  const lines = (build.log_tail ?? "").split("\n").filter((l) => l.trim().length > 0);
  return (
    <>
      <div className="panel-body stack-tight">
        <span className="xs muted mono">
          build {build.duration_s.toFixed(1)} s · {build.attempts ?? 1} {(build.attempts ?? 1) === 1 ? "attempt" : "attempts"}
        </span>
        {!build.ok && build.error ? <StepError error={build.error} /> : null}
      </div>
      {lines.length > 0 ? (
        <div className="log" tabIndex={0} aria-label="Build log tail">
          {lines.slice(-40).map((l, i) => (
            <div key={i}>{l}</div>
          ))}
        </div>
      ) : null}
    </>
  );
}
