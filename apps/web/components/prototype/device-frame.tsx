"use client";

import { Monitor, Smartphone } from "lucide-react";
import type { ReactNode } from "react";

export type Device = "desktop" | "mobile";

/** Segmented control, not a select. */
export function DeviceToggle({ value, onChange }: { value: Device; onChange: (d: Device) => void }) {
  return (
    <div className="seg" role="group" aria-label="Viewport">
      <button type="button" aria-pressed={value === "desktop"} aria-label="Desktop" onClick={() => onChange("desktop")}>
        <Monitor className="icon" aria-hidden="true" />
      </button>
      <button type="button" aria-pressed={value === "mobile"} aria-label="Phone" onClick={() => onChange("mobile")}>
        <Smartphone className="icon" aria-hidden="true" />
      </button>
    </div>
  );
}

export function DeviceFrame({ device, url, children }: { device: Device; url: string; children: ReactNode }) {
  return (
    <div className="frame-wrap">
      <div className={device === "mobile" ? "device mobile" : "device"} data-testid="device">
        <div className="device-bar">
          <span className="url">{url.replace(/^https?:\/\//, "")}</span>
        </div>
        {children}
      </div>
    </div>
  );
}
