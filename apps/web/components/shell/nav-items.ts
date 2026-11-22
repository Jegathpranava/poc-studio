import { LayoutTemplate, List, Plus, SlidersHorizontal, type LucideIcon } from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  /** Path prefixes that mark this item as current. */
  match: (pathname: string) => boolean;
}

export const NAV_ITEMS: NavItem[] = [
  {
    href: "/",
    label: "Runs",
    icon: List,
    match: (p) => p === "/" || (p.startsWith("/runs") && !p.startsWith("/runs/new")),
  },
  { href: "/runs/new", label: "New run", icon: Plus, match: (p) => p.startsWith("/runs/new") },
  { href: "/templates", label: "Templates", icon: LayoutTemplate, match: (p) => p.startsWith("/templates") },
  { href: "/settings", label: "Settings", icon: SlidersHorizontal, match: (p) => p.startsWith("/settings") },
];
