import type { Metadata } from "next";

import { AppShell } from "@/components/shell/app-shell";
import { AppToaster } from "@/components/shell/app-toaster";

import "./globals.css";

export const metadata: Metadata = {
  title: "PoC Studio",
  description: "Turn a meeting transcript into a scoped spec, a prototype, a repo and a pitch deck.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en">
      <body>
        <AppShell>{children}</AppShell>
        <AppToaster />
      </body>
    </html>
  );
}
