"use client";

import { Plug } from "lucide-react";
import { useEffect, useState } from "react";

import { notify } from "@/components/shell/notify";
import { PageHead } from "@/components/shell/page-head";
import { settingsApi, type SettingsData, type SettingsPatch } from "@/lib/share-api";

import { KeyStatus } from "./key-status";

export interface Draft {
  base_url: string;
  fast_model: string;
  smart_model: string;
  polish_model: string;
  run_limit_usd: string;
  monthly_cap_usd: string;
  hours_saved_per_run: string;
  retention_days: string;
}

function toDraft(s: SettingsData): Draft {
  return {
    base_url: s.gateway.base_url,
    fast_model: s.gateway.fast_model,
    smart_model: s.gateway.smart_model,
    polish_model: s.gateway.polish_model,
    run_limit_usd: String(s.budget.run_limit_usd),
    monthly_cap_usd: String(s.budget.monthly_cap_usd),
    hours_saved_per_run: String(s.budget.hours_saved_per_run),
    retention_days: String(s.retention_days),
  };
}

/** Turns the draft into a patch, or the first field error. Amounts must be positive, retention a whole number. */
export function buildPatch(d: Draft): { patch: SettingsPatch } | { error: string; field: keyof Draft } {
  const num = (v: string) => (v.trim() === "" ? Number.NaN : Number(v));
  const run = num(d.run_limit_usd);
  const cap = num(d.monthly_cap_usd);
  const hours = num(d.hours_saved_per_run);
  const days = num(d.retention_days);
  if (!/^https?:\/\/\S+$/.test(d.base_url.trim())) {
    return { error: "Enter a URL that starts with http:// or https://", field: "base_url" };
  }
  for (const f of ["fast_model", "smart_model", "polish_model"] as const) {
    if (!d[f].trim()) return { error: "Enter a model name", field: f };
  }
  if (!(run > 0)) return { error: "Enter an amount above 0", field: "run_limit_usd" };
  if (!(cap > 0)) return { error: "Enter an amount above 0", field: "monthly_cap_usd" };
  if (!(hours >= 0)) return { error: "Enter 0 or more hours", field: "hours_saved_per_run" };
  if (!Number.isInteger(days) || days < 0) {
    return { error: "Enter a whole number of days, 0 to keep everything", field: "retention_days" };
  }
  return {
    patch: {
      gateway: {
        base_url: d.base_url.trim(),
        fast_model: d.fast_model.trim(),
        smart_model: d.smart_model.trim(),
        polish_model: d.polish_model.trim(),
      },
      budget: { run_limit_usd: run, monthly_cap_usd: cap, hours_saved_per_run: hours },
      retention_days: days,
    },
  };
}

export function SettingsForm() {
  const [data, setData] = useState<SettingsData | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [fieldError, setFieldError] = useState<{ field: keyof Draft; message: string } | null>(null);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);

  useEffect(() => {
    settingsApi
      .get()
      .then((s) => {
        setData(s);
        setDraft(toDraft(s));
      })
      .catch((e: unknown) => setLoadError(e instanceof Error ? e.message : "Could not load the settings."));
  }, []);

  if (loadError) {
    return (
      <section className="screen">
        <PageHead title="Settings" />
        <div className="banner err" role="alert">
          <div className="grow">{loadError}</div>
        </div>
      </section>
    );
  }
  if (!data || !draft) {
    return (
      <section className="screen" aria-busy="true">
        <PageHead title="Settings" description="Keys are read from .env and never shown." />
        <div className="panel">
          <div className="panel-body stack">
            <span className="sk" style={{ width: "60%" }} />
            <span className="sk" style={{ width: "40%" }} />
          </div>
        </div>
      </section>
    );
  }

  const set = (key: keyof Draft) => (e: React.ChangeEvent<HTMLInputElement>) => {
    setDraft({ ...draft, [key]: e.target.value });
    if (fieldError?.field === key) setFieldError(null);
  };
  const err = (key: keyof Draft) => (fieldError?.field === key ? fieldError.message : null);

  async function save() {
    if (!draft) return;
    const built = buildPatch(draft);
    if ("error" in built) {
      setFieldError({ field: built.field, message: built.error });
      return;
    }
    setSaving(true);
    try {
      const next = await settingsApi.put(built.patch);
      setData(next);
      setDraft(toDraft(next));
      notify.success("Settings saved");
    } catch (e) {
      notify.error("Could not save the settings", e instanceof Error ? e.message : undefined);
    } finally {
      setSaving(false);
    }
  }

  async function testGateway() {
    setTesting(true);
    try {
      const res = await settingsApi.testGateway();
      if (res.ok) notify.success("Gateway connected", res.models.length ? res.models.join(", ") : undefined);
      else notify.error("Gateway not reachable", res.error ?? undefined);
    } catch (e) {
      notify.error("Gateway not reachable", e instanceof Error ? e.message : undefined);
    } finally {
      setTesting(false);
    }
  }

  const field = (key: keyof Draft, label: string, hint?: string, full = false) => (
    <div className={`field${full ? " full" : ""}${err(key) ? " error" : ""}`}>
      <label htmlFor={`s-${key}`}>{label}</label>
      <input
        id={`s-${key}`}
        className="input mono"
        value={draft[key]}
        onChange={set(key)}
        aria-invalid={err(key) ? true : undefined}
        aria-describedby={`s-${key}-hint`}
      />
      <span className="hint" id={`s-${key}-hint`}>
        {err(key) ?? hint}
      </span>
    </div>
  );

  return (
    <section className="screen">
      <PageHead
        title="Settings"
        description="Keys are read from .env and never shown."
        actions={
          <button type="button" className="btn primary" onClick={save} disabled={saving}>
            Save settings
          </button>
        }
      />
      <div className="grid-2">
        <div className="stack">
          <div className="panel">
            <div className="panel-head">
              <h2>Model gateway</h2>
              <span className={`status ${data.gateway.api_key_set ? "done" : "wait"}`}>
                {data.gateway.api_key_set ? "Key set" : "No key"}
              </span>
            </div>
            <div className="panel-body form-grid">
              {field("base_url", "Base URL", "A changed URL takes effect after the API restarts.", true)}
              {field("fast_model", "Extraction model", "Free")}
              {field("smart_model", "Architecture and code model", "Free")}
              {field("polish_model", "Deck polish model", "The only paid call, about $0.01 per run", true)}
              <div className="field full">
                <span className="label">API key</span>
                <KeyStatus name="OPENAI_API_KEY" isSet={data.gateway.api_key_set}>
                  <button type="button" className="btn sm" onClick={testGateway} disabled={testing}>
                    <Plug className="icon" aria-hidden="true" />
                    Test
                  </button>
                </KeyStatus>
              </div>
            </div>
          </div>
        </div>
        <div className="stack">
          <div className="panel">
            <div className="panel-head">
              <h2>GitHub</h2>
              <span className="status done">{data.github.mode === "live" ? "Live" : "Mock mode"}</span>
            </div>
            <div className="panel-body">
              <KeyStatus name="GITHUB_TOKEN" isSet={data.github.token_set} />
              <div className="switch">
                <div className="small">
                  <b>New client repos are private</b>
                </div>
                <button type="button" className="sw" role="switch" aria-checked="true" aria-label="Private by default" disabled />
              </div>
            </div>
          </div>
          <div className="panel">
            <div className="panel-head">
              <h2>Budget</h2>
            </div>
            <div className="panel-body form-grid">
              {field("run_limit_usd", "Paid limit per run (USD)")}
              {field("monthly_cap_usd", "Monthly cap (USD)")}
              {field(
                "hours_saved_per_run",
                "Hours saved per run",
                "Used for the hours-saved counter. From the problem statement: 4 to 6 h of scoping per prospect.",
                true,
              )}
            </div>
          </div>
          <div className="panel">
            <div className="panel-head">
              <h2>Data retention</h2>
            </div>
            <div className="panel-body form-grid">
              {field(
                "retention_days",
                "Delete uploaded inputs after (days)",
                "0 keeps everything. Generated files are always kept.",
                true,
              )}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
