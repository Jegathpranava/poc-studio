"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { Brand } from "./brand";
import { BudgetMeter } from "./budget-meter";
import { NAV_ITEMS } from "./nav-items";

export function Rail() {
  const pathname = usePathname();
  return (
    <aside className="rail" aria-label="Main">
      <Brand />
      {NAV_ITEMS.map(({ href, label, icon: Icon, match }) => (
        <Link key={href} href={href} title={label} aria-current={match(pathname) ? "page" : undefined}>
          <Icon className="icon" aria-hidden="true" />
          <span>{label}</span>
        </Link>
      ))}
      <div className="spacer" />
      <BudgetMeter />
    </aside>
  );
}
