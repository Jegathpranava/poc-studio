"use client";

import { Coins } from "lucide-react";
import { useState } from "react";

import { formatUsd } from "@/components/runs/format";
import { notify } from "@/components/shell/notify";
import { api, ApiError } from "@/lib/api";
import { raiseTarget } from "@/lib/revise";

import { useRun } from "./run-context";

interface BannerProps {
  limitUsd: number;
  busy?: boolean;
  onRaise: (to: number) => void;
  onFreeModel: () => void;
}

/** Shown while a run is `paused_budget`. Nothing is lost: the run continues from its checkpoint. */
export function BudgetBanner({ limitUsd, busy = false, onRaise, onFreeModel }: BannerProps) {
  const target = raiseTarget(limitUsd);
  return (
    <div className="banner warn" role="status" data-testid="budget-banner">
      <Coins className="icon" aria-hidden="true" />
      <div className="grow">
        <b>Paused: this run reached its {formatUsd(limitUsd)} paid limit.</b>
        <p className="muted">
          Pitch and Docs needs a little more to polish the deck. You can raise the limit for this run or finish the deck
          with the free model. Nothing already spent is lost.
        </p>
        <div className="actions">
          {target !== null ? (
            <button type="button" className="btn sm" disabled={busy} onClick={() => onRaise(target)}>
              Raise to {formatUsd(target)} for this run
            </button>
          ) : null}
          <button type="button" className="btn sm" disabled={busy} onClick={onFreeModel}>
            Use the free model
          </button>
        </div>
      </div>
    </div>
  );
}

/** The banner wired to the run: reads the status and limit from the run context. */
export function RunBudgetBanner() {
  const { runId, status, detail, reload } = useRun();
  const [busy, setBusy] = useState(false);
  if (status !== "paused_budget" || !detail) return null;

  const act = async (body: { budget_usd?: number; use_free_model?: boolean }, title: string, description: string) => {
    setBusy(true);
    try {
      await api.runs.budget(runId, body);
      notify.success(title, description);
      reload();
    } catch (e) {
      notify.error("Could not resume the run", e instanceof ApiError ? e.message : "Unknown error.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <BudgetBanner
      limitUsd={detail.budget_usd}
      busy={busy}
      onRaise={(to) =>
        act({ budget_usd: to }, `Budget raised to ${formatUsd(to)} for this run`, "Pitch and Docs continues.")
      }
      onFreeModel={() =>
        act({ use_free_model: true }, "Using the free model", "The deck keeps its drafted titles and captions.")
      }
    />
  );
}
