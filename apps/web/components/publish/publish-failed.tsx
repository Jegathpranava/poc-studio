import { CircleAlert } from "lucide-react";
import Link from "next/link";

import { PageHead } from "@/components/shell/page-head";

/** The publish step failed after Gate 2. Retrying a failed step arrives with the retry endpoint. */
export function PublishFailed({ runId, message }: { runId: string; message: string }) {
  return (
    <section className="screen" data-testid="publish-failed">
      <PageHead title="Publishing failed" description="Nothing was delivered. The prototype and deck are still available." />
      <div className="banner err" role="alert">
        <CircleAlert className="icon" aria-hidden="true" />
        <div className="grow">
          <b>The repo could not be published.</b>
          <p className="muted" data-testid="publish-error">
            {message}
          </p>
          <div className="actions">
            <Link className="btn sm" href={`/runs/${runId}`}>
              Open the timeline
            </Link>
          </div>
        </div>
      </div>
    </section>
  );
}
