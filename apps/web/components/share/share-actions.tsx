"use client";

import { Copy, Download } from "lucide-react";
import { useState } from "react";

import { notify } from "@/components/shell/notify";
import { shareApi, shareLink } from "@/lib/share-api";

const COPY_NOTE = "This link works on this machine only. Send the zip to the client.";

/** The two share actions for Gate 2 and the Delivered view. Nothing is hosted: the zip is what the client gets. */
export function ShareActions({ runId }: { runId: string }) {
  const [busy, setBusy] = useState<"zip" | "link" | null>(null);

  async function downloadZip() {
    setBusy("zip");
    try {
      const made = await shareApi.exportZip(runId);
      window.location.assign(shareApi.asset(made.download_url));
      notify.success("Share zip ready", made.warnings.length ? `${made.warnings.length} warning(s) in the manifest` : undefined);
    } catch (e) {
      notify.error("Could not build the share zip", e instanceof Error ? e.message : undefined);
    } finally {
      setBusy(null);
    }
  }

  async function copyLink() {
    setBusy("link");
    try {
      const made = await shareApi.createToken(runId);
      await navigator.clipboard.writeText(shareLink(window.location.origin, made.path));
      notify.success("Link copied", COPY_NOTE);
    } catch (e) {
      notify.error("Could not copy the link", e instanceof Error ? e.message : undefined);
    } finally {
      setBusy(null);
    }
  }

  return (
    <div className="actions">
      <button type="button" className="btn" onClick={downloadZip} disabled={busy !== null}>
        <Download className="icon" aria-hidden="true" />
        Download share zip
      </button>
      <button type="button" className="btn primary" onClick={copyLink} disabled={busy !== null}>
        <Copy className="icon" aria-hidden="true" />
        Copy client share link
      </button>
    </div>
  );
}
