export const ACCEPTED_EXTENSIONS = [".txt", ".vtt", ".md", ".docx", ".pdf"] as const;
export const MAX_FILE_BYTES = 20 * 1024 * 1024;

export interface Rejection {
  name: string;
  reason: string;
}

export function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

/** Splits dropped or chosen files into the ones to keep and the ones to refuse, with a reason each. */
export function checkFiles(
  incoming: File[],
  existing: File[] = [],
): { accepted: File[]; rejected: Rejection[] } {
  const accepted: File[] = [];
  const rejected: Rejection[] = [];
  const seen = new Set(existing.map((f) => `${f.name}:${f.size}`));
  for (const file of incoming) {
    const ext = file.name.slice(file.name.lastIndexOf(".")).toLowerCase();
    if (!(ACCEPTED_EXTENSIONS as readonly string[]).includes(ext)) {
      rejected.push({ name: file.name, reason: `is not a supported type. Use ${ACCEPTED_EXTENSIONS.join(", ")}.` });
    } else if (file.size > MAX_FILE_BYTES) {
      rejected.push({ name: file.name, reason: `is ${formatBytes(file.size)}, over the 20 MB limit.` });
    } else if (file.size === 0) {
      rejected.push({ name: file.name, reason: "is empty." });
    } else if (!seen.has(`${file.name}:${file.size}`)) {
      seen.add(`${file.name}:${file.size}`);
      accepted.push(file);
    }
  }
  return { accepted, rejected };
}
