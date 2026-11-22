import type { ReactNode } from "react";
import Link from "next/link";
import "./kit/product.css";
import "./kit/icons.css";
import "./globals.css";

export const metadata = { title: "Northline Freight", description: "Sector starter for logistics" };

const nav = [
  { href: "/", label: "Overview", icon: "layout-dashboard" },
  { href: "/", label: "Shipments", icon: "package" },
  { href: "/", label: "Fleet", icon: "truck" },
  { href: "/", label: "Routes", icon: "route" },
  { href: "/", label: "Reports", icon: "file-text" },
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="pf">
          <div className="lgx">
            <div className="shell">
              <aside className="rail">
                <div className="rail-brand">
                  <span className="brand-mark"><span className="ic ic-truck" /></span>
                  <span>Northline Freight</span>
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
                  <span className="topbar-title">Northline Freight</span>
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
