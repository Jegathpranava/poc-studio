import type { components } from "./api-types";
import type { Architecture } from "./architecture";
import type { Requirements } from "./requirements";

export type RunSummary = components["schemas"]["RunSummary"];
export type RunDetail = components["schemas"]["RunDetail"];
export type RunStatus = RunSummary["status"];
export type HealthResponse = components["schemas"]["HealthResponse"];
export type GateDecisionResponse = components["schemas"]["GateDecisionResponse"];
export type FileNode = components["schemas"]["FileNode"];
export type PreviewInfo = components["schemas"]["PreviewInfo"];
export type PublishStatus = components["schemas"]["PublishStatus"];
export type PublishResult = components["schemas"]["PublishResult"];

/** Gate 2 options as sent to the API. `repo_name` is validated by the same pattern on the server. */
export interface PublishOptions {
  repo_name: string;
  private: boolean;
  open_issues: boolean;
  add_ci: boolean;
}

export interface QaCheck {
  name: string;
  ok: boolean;
  detail: string;
  owner_agent: string;
  report_only: boolean;
}

/** `qa_report.v<N>.json`, written by the QA Reviewer. */
export interface QaReport {
  checks: QaCheck[];
  passed: string[];
  failed: string[];
  send_back: string | null;
  block_publish: boolean;
  sent_back_count: number;
}

/** `build.json`, written by the Prototype Builder. `error` is the structured build error. */
export interface BuildInfo {
  ok: boolean;
  duration_s: number;
  attempts?: number | null;
  install_s?: number | null;
  error?: { file?: string | null; line?: number | null; col?: number | null; message: string; excerpt?: string | null } | null;
  log_tail?: string;
}

/** Answer of the revise, retry and budget routes (`routes/revise.py`). */
export type ReviseResponse = components["schemas"]["ReviseResponse"];

/** The artifact pages that can ask for changes at Gate 2 (the brief has its own Gate 1 flow). */
export type RevisableType = "architecture" | "prototype" | "deck";

export const BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export interface FieldError {
  loc: (string | number)[];
  msg: string;
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
    readonly fields: FieldError[] = [],
  ) {
    super(message);
    this.name = "ApiError";
  }
}

/** Reads the `detail` of a FastAPI error: a string, or a list of `{loc, msg}` field errors. */
async function failure(res: Response): Promise<ApiError> {
  let detail: unknown;
  try {
    detail = ((await res.json()) as { detail?: unknown }).detail;
  } catch {
    detail = undefined;
  }
  if (typeof detail === "string") return new ApiError(detail, res.status);
  if (Array.isArray(detail)) {
    const fields = detail
      .filter((d): d is FieldError => typeof d === "object" && d !== null && "msg" in d)
      .map((d) => ({ loc: Array.isArray(d.loc) ? d.loc : [], msg: String(d.msg) }));
    return new ApiError("Some fields are not valid.", res.status, fields);
  }
  return new ApiError(`The API answered ${res.status}.`, res.status);
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, { cache: "no-store", ...init });
  } catch {
    throw new ApiError("The PoC Studio API is not reachable.");
  }
  if (!res.ok) throw await failure(res);
  return (await res.json()) as T;
}

const json = (body: unknown): RequestInit => ({
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(body),
});

export interface Chapter {
  t: number;
  title: string;
}

export interface ArtifactJson<T> {
  type: string;
  version: number;
  data: T;
}

export const api = {
  health: () => request<HealthResponse>("/api/health"),
  runs: {
    list: () => request<RunSummary[]>("/api/runs"),
    get: (id: string) => request<RunDetail>(`/api/runs/${id}`),
    create: (form: FormData) => request<{ id: string }>("/api/runs", { method: "POST", body: form }),
    requirements: (id: string) => request<ArtifactJson<Requirements>>(`/api/runs/${id}/artifacts/requirements`),
    architecture: (id: string) => request<ArtifactJson<Architecture>>(`/api/runs/${id}/artifacts/architecture`),
    videoChapters: (id: string) => request<Chapter[]>(`/api/runs/${id}/video/chapters`),
    videoUrl: (id: string) => `${BASE_URL}/api/runs/${id}/video`,
    deckUrl: (id: string, download = false) => `${BASE_URL}/api/runs/${id}/deck.html${download ? "?download=true" : ""}`,
    pptxUrl: (id: string) => `${BASE_URL}/api/runs/${id}/deck.pptx`,
    docUrl: (id: string, name: "exec-summary" | "user-flows") => `${BASE_URL}/api/runs/${id}/docs/${name}`,
    architectureMarkdownUrl: (id: string) => `${BASE_URL}/api/runs/${id}/artifacts/architecture/markdown`,
    files: (id: string) => request<FileNode[]>(`/api/runs/${id}/files`),
    build: (id: string) => request<BuildInfo>(`/api/runs/${id}/build`),
    /** Starts (or reuses) the preview server. Calling it again counts as activity for the idle timer. */
    startPreview: (id: string) => request<PreviewInfo>(`/api/runs/${id}/preview`, json({})),
    qaReport: (id: string) => request<ArtifactJson<QaReport>>(`/api/runs/${id}/artifacts/qa_report`),
    publish: (id: string) => request<PublishStatus>(`/api/runs/${id}/publish`),
    decidePublish: (id: string, options: PublishOptions) =>
      request<GateDecisionResponse>(`/api/runs/${id}/gates/publish`, json({ decision: "approve", options })),
    /** Request changes: only the artifact's owning agent reruns. Allowed while the run waits at Gate 2. */
    revise: (id: string, type: RevisableType, note: string) =>
      request<ReviseResponse>(`/api/runs/${id}/artifacts/${type}/revise`, json({ note })),
    /** Retry a failed port build (at Gate 2) or resume a failed run. */
    retry: (id: string, body: { note?: string; attempts?: number } = {}) =>
      request<ReviseResponse>(`/api/runs/${id}/retry`, json(body)),
    /** Resume a run paused on its budget: raise the limit and/or finish the deck with the free model. */
    budget: (id: string, body: { budget_usd?: number; use_free_model?: boolean }) =>
      request<ReviseResponse>(`/api/runs/${id}/budget`, json(body)),
    decideScope: (id: string, body: { decision: "approve" | "changes"; edits?: Requirements; note?: string }) =>
      request<GateDecisionResponse>(`/api/runs/${id}/gates/scope`, json(body)),
  },
};
