"use client";

import { useEffect, useState } from "react";

import { PageHead } from "@/components/shell/page-head";
import { buildRateLabel, templatesApi, type TemplateStat } from "@/lib/share-api";

const LABELS: Record<string, string> = {
  logistics: "Logistics dispatch",
  healthcare: "Healthcare intake",
  "e-commerce": "E-commerce storefront",
  fintech: "Fintech onboarding",
};

export function TemplatesView() {
  const [kits, setKits] = useState<TemplateStat[] | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    templatesApi
      .list()
      .then(setKits)
      .catch((e: unknown) => setError(e instanceof Error ? e.message : "Could not load the templates."));
  }, []);

  return (
    <section className="screen">
      <PageHead
        title="Sector templates"
        description="The starting point the Prototype Builder adapts. Edit them in templates/."
      />
      {error ? (
        <div className="banner err" role="alert">
          <div className="grow">{error}</div>
        </div>
      ) : !kits ? (
        <div className="panel" aria-busy="true">
          <div className="panel-body stack">
            <span className="sk" style={{ width: "50%" }} />
            <span className="sk" style={{ width: "70%" }} />
          </div>
        </div>
      ) : (
        <div className="panel">
          <table className="table responsive" aria-label="Sector templates">
            <thead>
              <tr>
                <th>Template</th>
                <th>Screens</th>
                <th>First-time builds</th>
                <th>Used</th>
              </tr>
            </thead>
            <tbody>
              {kits.map((k) => (
                <tr key={k.sector}>
                  <td>
                    <b>{LABELS[k.sector] ?? k.sector}</b>
                    <div className="xs muted mono">{k.sector}</div>
                  </td>
                  <td className="hide-sm small">{k.screens}</td>
                  <td className="mono num small">{buildRateLabel(k)}</td>
                  <td className="hide-sm mono num small">{k.runs_used}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
