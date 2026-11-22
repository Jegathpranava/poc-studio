import type { components } from "./api-types";
import type { Architecture } from "./architecture";
import type { Requirements } from "./requirements";

export type RunSummary = components["schemas"]["RunSummary"];
export type RunDetail = components["schemas"]["RunDetail"];
export type RunStatus = RunSummary["status"];
export type HealthResponse = components["schemas"]["HealthResponse"];
export type GateDecisionResponse = components["schemas"]["GateDecisionResponse"];

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
    architectureMarkdownUrl: (id: string) => `${BASE_URL}/api/runs/${id}/artifacts/architecture/markdown`,
    decideScope: (id: string, body: { decision: "approve" | "changes"; edits?: Requirements; note?: string }) =>
      request<GateDecisionResponse>(`/api/runs/${id}/gates/scope`, json(body)),
  },
};
