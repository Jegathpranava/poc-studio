"use client";

import { useEffect, useId, useState } from "react";

const token = (name: string): string => getComputedStyle(document.documentElement).getPropertyValue(name).trim();

/** Mermaid theme variables read from the CSS tokens at runtime, so the diagram follows the design system. */
function themeVariables(): Record<string, string> {
  return {
    fontFamily: token("--font-body"),
    background: token("--color-surface"),
    primaryColor: token("--color-primary-soft"),
    primaryTextColor: token("--color-fg"),
    primaryBorderColor: token("--color-primary"),
    secondaryColor: token("--color-surface"),
    tertiaryColor: token("--color-sunken"),
    lineColor: token("--color-muted"),
    textColor: token("--color-fg"),
    mainBkg: token("--color-primary-soft"),
    nodeBorder: token("--color-primary"),
    clusterBkg: token("--color-sunken"),
    clusterBorder: token("--color-border-strong"),
    edgeLabelBackground: token("--color-surface"),
  };
}

type Result = { state: "loading" } | { state: "ready"; svg: string } | { state: "error"; message: string };

export function MermaidDiagram({ source, label }: { source: string; label: string }) {
  const id = `mmd-${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  const [result, setResult] = useState<Result>({ state: "loading" });

  useEffect(() => {
    let live = true;
    (async () => {
      try {
        const { default: mermaid } = await import("mermaid"); // lazy: the library is large
        mermaid.initialize({
          startOnLoad: false,
          securityLevel: "strict",
          theme: "base",
          themeVariables: themeVariables(),
        });
        const { svg } = await mermaid.render(id, source);
        if (live) setResult({ state: "ready", svg });
      } catch (e) {
        if (live) {
          setResult({ state: "error", message: e instanceof Error ? e.message : "Could not render the diagram." });
        }
      }
    })();
    return () => {
      live = false;
    };
  }, [id, source]);

  if (result.state === "error") {
    return (
      <div className="diagram-fallback" role="alert">
        <p className="small muted">The diagram could not be drawn ({result.message}). The Mermaid source is below.</p>
        <pre className="mono small">{source}</pre>
      </div>
    );
  }
  if (result.state === "loading") {
    return <span className="sk diagram-sk" aria-busy="true" aria-label="Drawing the diagram" />;
  }
  return (
    <div
      className="diagram"
      role="img"
      aria-label={label}
      data-testid="diagram"
      dangerouslySetInnerHTML={{ __html: result.svg }}
    />
  );
}
