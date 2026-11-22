import type { components } from "./api-types";

export type RunSummary = components["schemas"]["RunSummary"];
export type HealthResponse = components["schemas"]["HealthResponse"];

const BASE_URL = (process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function get<T>(path: string): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, { cache: "no-store" });
  } catch {
    throw new ApiError("The PoC Studio API is not reachable.");
  }
  if (!res.ok) throw new ApiError(`The API answered ${res.status}.`, res.status);
  return (await res.json()) as T;
}

export const api = {
  health: () => get<HealthResponse>("/api/health"),
  runs: {
    list: () => get<RunSummary[]>("/api/runs"),
  },
};
