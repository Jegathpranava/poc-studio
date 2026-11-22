"use client";

import { Toaster, type SileoOptions } from "sileo";

const TOAST_OPTIONS: Partial<SileoOptions> = { fill: "var(--toast-fill)", duration: 4000 };

export function AppToaster() {
  return <Toaster position="bottom-right" options={TOAST_OPTIONS} />;
}
