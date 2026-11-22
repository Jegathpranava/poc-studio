import { describe, expect, it } from "vitest";

import { canCreate, filterSectors } from "@/lib/sectors";
import { MAX_FILE_BYTES, checkFiles } from "@/lib/upload";

const file = (name: string, size = 10) => new File([new Uint8Array(size)], name);

describe("upload checks", () => {
  it("accepts the five document types, several at once", () => {
    const names = ["a.txt", "b.VTT", "c.md", "d.docx", "e.pdf"];
    const { accepted, rejected } = checkFiles(names.map((n) => file(n)));
    expect(accepted).toHaveLength(5);
    expect(rejected).toEqual([]);
  });

  it("refuses other types, empty files and files over 20 MB, with a reason", () => {
    const big = file("big.pdf", 1);
    Object.defineProperty(big, "size", { value: MAX_FILE_BYTES + 1 });
    const { accepted, rejected } = checkFiles([file("notes.exe"), file("empty.txt", 0), big, file("ok.txt")]);
    expect(accepted.map((f) => f.name)).toEqual(["ok.txt"]);
    expect(rejected.map((r) => r.name)).toEqual(["notes.exe", "empty.txt", "big.pdf"]);
    expect(rejected[0].reason).toContain("not a supported type");
    expect(rejected[2].reason).toContain("over the 20 MB limit");
  });

  it("skips a file that was already added", () => {
    const first = file("a.txt");
    expect(checkFiles([file("a.txt")], [first]).accepted).toEqual([]);
  });
});

describe("sector search", () => {
  it("filters by label and offers Create for new text only", () => {
    expect(filterSectors("fin").map((s) => s.value)).toEqual(["fintech"]);
    expect(filterSectors("").length).toBe(4);
    expect(canCreate("Fintech")).toBe(false);
    expect(canCreate("")).toBe(false);
    expect(canCreate("Insurance")).toBe(true);
  });
});
