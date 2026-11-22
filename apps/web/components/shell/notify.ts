"use client";

import { sileo } from "sileo";

/** Toasts go through the one <AppToaster /> mounted in the root layout. */
export const notify = {
  success: (title: string, description?: string) => sileo.success({ title, description }),
  error: (title: string, description?: string) => sileo.error({ title, description }),
  info: (title: string, description?: string) => sileo.info({ title, description }),
};
