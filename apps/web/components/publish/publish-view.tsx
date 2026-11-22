"use client";

import { CircleAlert, Clock, LoaderCircle } from "lucide-react";
import { useEffect, useState, type ReactNode } from "react";

import { useRun } from "@/components/run/run-context";
import { notify } from "@/components/shell/notify";
import { PageHead } from "@/components/shell/page-head";
import { api, type PublishStatus } from "@/lib/api";

import { DeliveredView } from "./delivered-view";
import { Gate2View } from "./gate2-view";
import { PublishFailed } from "./publish-failed";

const POLL_MS = 1500;

function Message({ icon, title, body }: { icon: ReactNode; title: string; body: string }) {
  return (
    <section className="screen">
      <PageHead title="Publish" />
      <div className="panel">
        <div className="empty">
          {icon}
          <h2>{title}</h2>
          <p>{body}</p>
        </div>
      </div>
    </section>
  );
}

/** Gate 2 while the run waits for the owner, then Delivered (or the failure) once the publish ran. */
export function PublishView() {
  const { runId, status, detail, detailError, reload } = useRun();
  const [following, setFollowing] = useState(false);
  const [pub, setPub] = useState<PublishStatus | null>(null);
  const [tick, setTick] = useState(0);

  const settled = status === "delivered" || status === "failed";
  const wanted = following || settled;

  useEffect(() => {
    if (!wanted) return;
    let live = true;
    let timer: ReturnType<typeof setTimeout> | undefined;
    api.runs
      .publish(runId)
      .then((p) => {
        if (!live) return;
        setPub(p);
        if (p.status === "delivered" || p.status === "failed") {
          if (following) {
            if (p.status === "delivered") notify.success("Published", "The deliverables are listed below.");
            else notify.error("Publishing failed", p.error ?? undefined);
            setFollowing(false);
          }
          reload();
        } else {
          timer = setTimeout(() => setTick((n) => n + 1), POLL_MS);
        }
      })
      .catch(() => {
        if (live) timer = setTimeout(() => setTick((n) => n + 1), POLL_MS * 2);
      });
    return () => {
      live = false;
      clearTimeout(timer);
    };
  }, [runId, wanted, following, status, tick, reload]);

  if (detailError) {
    return (
      <section className="screen">
        <PageHead title="Publish" />
        <div className="banner err" role="alert">
          <CircleAlert className="icon" aria-hidden="true" />
          <div className="grow">
            <b>The run could not be loaded.</b>
            <p className="muted">{detailError.message}</p>
          </div>
        </div>
      </section>
    );
  }
  if (!detail) {
    return (
      <section className="screen">
        <PageHead title="Publish" />
        <div className="panel">
          <div className="panel-body" aria-busy="true" aria-label="Loading the run">
            <span className="sk" style={{ width: "100%", height: 160 }} />
          </div>
        </div>
      </section>
    );
  }
  if (status === "waiting_gate2" && !following) {
    return <Gate2View runId={runId} detail={detail} onSubmitted={() => setFollowing(true)} />;
  }
  if (status === "delivered" && pub?.status === "delivered") {
    return <DeliveredView runId={runId} detail={detail} status={pub} />;
  }
  if (status === "failed" && pub?.status === "failed") {
    return <PublishFailed runId={runId} message={pub.error ?? "The run failed before it was delivered."} />;
  }
  if (following || (status === "running" && pub?.status === "publishing")) {
    return (
      <section className="screen" data-testid="publishing">
        <PageHead title="Publishing" description="Creating the repo, pushing the code and opening issues." />
        <div className="panel">
          <div className="panel-body publishing" aria-busy="true">
            <LoaderCircle className="icon" aria-hidden="true" />
            <span className="small">This takes a few seconds.</span>
          </div>
        </div>
      </section>
    );
  }
  if (settled) {
    return (
      <Message
        icon={<Clock aria-hidden="true" />}
        title="Loading the result"
        body="The publish details appear here in a moment."
      />
    );
  }
  return (
    <Message
      icon={<Clock aria-hidden="true" />}
      title="Available after QA passes and you reach Gate 2"
      body="This page fills in as the run reaches that step."
    />
  );
}
