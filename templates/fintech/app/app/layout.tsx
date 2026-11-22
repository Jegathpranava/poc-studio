import type { ReactNode } from "react";
import Link from "next/link";
import "./kit/product.css";
import "./kit/icons.css";
import "./globals.css";

export const metadata = { title: "Cedar Ledger", description: "Sector starter for fintech" };

const nav = [
  { href: "/", label: "Overview", icon: "layout-dashboard" },
  { href: "/", label: "Accounts", icon: "wallet" },
  { href: "/", label: "Transfers", icon: "trending-up" },
  { href: "/", label: "Cards", icon: "credit-card" },
  { href: "/", label: "Risk alerts", icon: "shield-check" },
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="pf">
          <div className="fnx">
            <div className="shell">
              <aside className="rail">
                <div className="rail-brand">
                  <span className="brand-mark"><span className="ic ic-wallet" /></span>
                  <span>Cedar Ledger</span>
                </div>
                {nav.map((n, i) => (
                  <Link key={n.label} href={n.href} className={"rail-link" + (i === 0 ? " is-active" : "")}>
                    <span className={"ic ic-" + n.icon} />
                    <span>{n.label}</span>
                  </Link>
                ))}
                <div className="rail-foot">Sample data, illustrative</div>
              </aside>
              <div className="main">
                <header className="topbar">
                  <span className="topbar-title">Cedar Ledger</span>
                  <div className="topbar-search"><span className="ic ic-search" /><span>Search</span></div>
                  <div className="topbar-actions"><span className="avatar">JM</span></div>
                </header>
                <main className="page">{children}</main>
              </div>
            </div>
          </div>
        </div>
      </body>
    </html>
  );
}
