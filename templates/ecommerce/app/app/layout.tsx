import type { ReactNode } from "react";
import Link from "next/link";
import "./kit/product.css";
import "./kit/icons.css";
import "./globals.css";

export const metadata = { title: "Marlow and Finch", description: "Sector starter for ecommerce" };

const nav = [
  { href: "/", label: "Overview", icon: "layout-dashboard" },
  { href: "/", label: "Orders", icon: "package" },
  { href: "/", label: "Products", icon: "tag" },
  { href: "/", label: "Customers", icon: "user" },
  { href: "/", label: "Reviews", icon: "star" },
];

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="pf">
          <div className="ecx">
            <div className="shell">
              <aside className="rail">
                <div className="rail-brand">
                  <span className="brand-mark"><span className="ic ic-shopping-cart" /></span>
                  <span>Marlow and Finch</span>
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
                  <span className="topbar-title">Marlow and Finch</span>
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
