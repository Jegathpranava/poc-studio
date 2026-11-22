export interface SectorOption {
  value: string;
  label: string;
  /** True for the four sectors that have a template. */
  template: boolean;
}

export const SECTORS: SectorOption[] = [
  { value: "logistics", label: "Logistics", template: true },
  { value: "healthcare", label: "Healthcare", template: true },
  { value: "e-commerce", label: "E-commerce", template: true },
  { value: "fintech", label: "Fintech", template: true },
];

export function sectorLabel(value: string): string {
  return SECTORS.find((s) => s.value === value)?.label ?? value;
}

/** Options that match the search text, in list order. */
export function filterSectors(query: string, options: SectorOption[] = SECTORS): SectorOption[] {
  const q = query.trim().toLowerCase();
  return q ? options.filter((s) => s.label.toLowerCase().includes(q)) : options;
}

/** The inline "Create" row shows only for text that is not already a sector. */
export function canCreate(query: string, options: SectorOption[] = SECTORS): boolean {
  const q = query.trim().toLowerCase();
  return q.length > 0 && !options.some((s) => s.label.toLowerCase() === q || s.value === q);
}
