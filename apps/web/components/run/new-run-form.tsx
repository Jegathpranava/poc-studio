"use client";

import { CircleAlert, Play } from "lucide-react";
import { useRouter } from "next/navigation";
import { useState, type FormEvent } from "react";

import { PageHead } from "@/components/shell/page-head";
import { notify } from "@/components/shell/notify";
import { api, ApiError } from "@/lib/api";

import { FileDrop } from "./file-drop";
import { DEFAULT_OPTIONS, OptionSwitches, type RunOptionsState } from "./option-switches";
import { SectorCombobox } from "./sector-combobox";
import { WhatHappensNext } from "./what-happens-next";

const RUN_LIMIT_USD = 0.05;

export function buildRunForm(files: File[], client: string, sector: string, options: RunOptionsState): FormData {
  const form = new FormData();
  for (const f of files) form.append("files", f, f.name);
  form.append("client", client.trim());
  if (sector) form.append("sector", sector);
  form.append("private_repo", String(options.privateRepo));
  form.append("record_video", String(options.recordVideo));
  form.append("export_pptx", String(options.exportPptx));
  form.append("mask_pii", String(options.maskPii));
  return form;
}

export function NewRunForm() {
  const router = useRouter();
  const [files, setFiles] = useState<File[]>([]);
  const [client, setClient] = useState("");
  const [sector, setSector] = useState("");
  const [options, setOptions] = useState<RunOptionsState>(DEFAULT_OPTIONS);
  const [submitting, setSubmitting] = useState(false);
  const [tried, setTried] = useState(false);
  const [failure, setFailure] = useState<string | null>(null);

  const fileError = tried && files.length === 0 ? "Add at least one file." : null;
  const clientError = tried && client.trim() === "" ? "Enter the client name." : null;

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setTried(true);
    setFailure(null);
    if (files.length === 0 || client.trim() === "") return;
    setSubmitting(true);
    try {
      const { id } = await api.runs.create(buildRunForm(files, client, sector, options));
      notify.success("Run started", "Agents are reading your files.");
      router.push(`/runs/${id}`);
    } catch (err) {
      setFailure(err instanceof ApiError ? err.message : "The run could not be started.");
      setSubmitting(false);
    }
  };

  return (
    <section className="screen">
      <PageHead
        title="New run"
        description="One input, seven agents, two checkpoints. About 5 minutes of agent time."
      />
      <form onSubmit={submit} noValidate>
        {failure ? (
          <div className="banner err" role="alert">
            <CircleAlert className="icon" aria-hidden="true" />
            <div className="grow">
              <b>The run did not start.</b>
              <p className="muted">{failure}</p>
            </div>
          </div>
        ) : null}
        <div className="grid-2">
          <div className="stack">
            <div className="panel">
              <div className="panel-head">
                <h2>Source</h2>
              </div>
              <div className="panel-body">
                <FileDrop files={files} onChange={setFiles} error={fileError} />
              </div>
            </div>
            <div className="panel">
              <div className="panel-head">
                <h2>Client</h2>
              </div>
              <div className="panel-body form-grid">
                <div className={`field${clientError ? " error" : ""}`}>
                  <label htmlFor="client">Client name</label>
                  <input
                    className="input"
                    id="client"
                    value={client}
                    autoComplete="off"
                    aria-invalid={clientError ? true : undefined}
                    onChange={(e) => setClient(e.target.value)}
                  />
                  {clientError ? <span className="hint">{clientError}</span> : null}
                </div>
                <SectorCombobox value={sector} onChange={setSector} />
              </div>
            </div>
          </div>
          <div className="stack">
            <OptionSwitches value={options} onChange={setOptions} limitUsd={RUN_LIMIT_USD} />
            <div className="panel">
              <div className="panel-body">
                <WhatHappensNext />
                <button type="submit" className="btn primary block note-box" disabled={submitting}>
                  <Play className="icon" aria-hidden="true" />
                  {submitting ? "Starting" : "Start run"}
                </button>
              </div>
            </div>
          </div>
        </div>
      </form>
    </section>
  );
}
