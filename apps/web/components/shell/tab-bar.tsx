"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { NAV_ITEMS } from "./nav-items";

export function TabBar() {
  const pathname = usePathname();
  return (
    <nav className="tabbar" aria-label="Main tabs">
      {NAV_ITEMS.map(({ href, label, icon: Icon, match }) => (
        <Link key={href} href={href} aria-current={match(pathname) ? "page" : undefined}>
          <Icon className="icon" aria-hidden="true" />
          {label}
        </Link>
      ))}
    </nav>
  );
}
