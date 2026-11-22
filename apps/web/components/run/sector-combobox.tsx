"use client";

import { ChevronDown } from "lucide-react";
import { useEffect, useId, useMemo, useRef, useState, type KeyboardEvent } from "react";

import { canCreate, filterSectors, sectorLabel } from "@/lib/sectors";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

type Row = { key: string; value: string; label: string; hint: string };

/** A searchable sector picker with an inline "Create" row. It is never a native select. */
export function SectorCombobox({ value, onChange }: Props) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");
  const [active, setActive] = useState(0);
  const root = useRef<HTMLDivElement>(null);
  const search = useRef<HTMLInputElement>(null);
  const labelId = useId();
  const listId = useId();

  const rows = useMemo<Row[]>(() => {
    const list: Row[] = [];
    if (!query.trim()) list.push({ key: "none", value: "", label: "Detect from the transcript", hint: "" });
    for (const s of filterSectors(query)) list.push({ key: s.value, value: s.value, label: s.label, hint: "template" });
    if (canCreate(query)) {
      list.push({ key: "create", value: query.trim(), label: `Create "${query.trim()}"`, hint: "uses the closest template" });
    }
    return list;
  }, [query]);

  useEffect(() => {
    if (!open) return;
    search.current?.focus();
    const away = (e: MouseEvent) => !root.current?.contains(e.target as Node) && setOpen(false);
    document.addEventListener("mousedown", away);
    return () => document.removeEventListener("mousedown", away);
  }, [open]);

  const pick = (row: Row) => {
    onChange(row.value);
    setOpen(false);
    setQuery("");
  };

  const onKey = (e: KeyboardEvent) => {
    if (!open) return;
    if (e.key === "Escape") setOpen(false);
    else if (e.key === "ArrowDown") {
      e.preventDefault();
      setActive((i) => Math.min(i + 1, rows.length - 1));
    } else if (e.key === "ArrowUp") {
      e.preventDefault();
      setActive((i) => Math.max(i - 1, 0));
    } else if (e.key === "Enter") {
      e.preventDefault();
      const row = rows[active];
      if (row) pick(row);
    }
  };

  return (
    <div className="field">
      <span className="label" id={labelId}>
        Sector
      </span>
      <div className={`combo${open ? " open" : ""}`} ref={root} onKeyDown={onKey}>
      <button
        type="button"
        className="combo-btn"
        aria-labelledby={labelId}
        aria-haspopup="listbox"
        aria-expanded={open}
        aria-controls={listId}
        onClick={() => {
          setOpen((o) => !o);
          setActive(0);
        }}
      >
        <span className="val">{value ? sectorLabel(value) : "Detect from the transcript"}</span>
        <ChevronDown className="icon" aria-hidden="true" />
      </button>
      {open ? (
        <div className="combo-pop" id={listId}>
          <input
            ref={search}
            value={query}
            placeholder="Search or create a sector"
            aria-label="Search sectors"
            onChange={(e) => {
              setQuery(e.target.value);
              setActive(0);
            }}
          />
          <div role="listbox" aria-labelledby={labelId}>
            {rows.map((row, i) => (
              <button
                key={row.key}
                type="button"
                role="option"
                className={`combo-opt${row.key === "create" ? " create" : ""}`}
                aria-selected={row.value === value && row.key !== "create"}
                data-active={i === active}
                onMouseEnter={() => setActive(i)}
                onClick={() => pick(row)}
              >
                <span>{row.label}</span>
                {row.hint ? <span className="xs">{row.hint}</span> : null}
              </button>
            ))}
            {rows.length === 0 ? <div className="combo-empty">No match.</div> : null}
          </div>
        </div>
      ) : null}
      </div>
      <span className="hint">Detected from the transcript when left empty. Change it if it is wrong.</span>
    </div>
  );
}
