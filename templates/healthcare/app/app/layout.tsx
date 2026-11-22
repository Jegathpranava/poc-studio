import type { ReactNode } from "react";
import Link from "next/link";
import "./kit/product.css";
import "./kit/icons.css";
import "./globals.css";

export const metadata = { title: "Larchmont Clinic", description: "Sector starter for healthcare" };

const nav = [
  { href: "/", label: "Overview", icon: "layout-dashboard" },
  { href: "/", label: "Appointments", icon: "calendar" },
  { href: "/", label: "Patients", icon: "user" },
  { href: "/", label: "Care plans", icon: "stethoscope" },
  { href: "/", label: "Prescriptions", icon: "pill" },
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="pf">
          <div className="hlx">
            <div className="shell">
              <aside className="rail">
                <div className="rail-brand">
                  <span className="brand-mark"><span className="ic ic-heart-pulse" /></span>
                  <span>Larchmont Clinic</span>
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
                  <span className="topbar-title">Larchmont Clinic</span>
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
