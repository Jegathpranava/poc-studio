import { ApiError, BASE_URL } from "./api";

// Fetch helpers for sharing, settings and templates. They live here because api.ts belongs to the run pages.

export interface ShareToken {
  token: string;
  path: string;
  expires_at: string;
}

export interface ShareExport {
  run_id: string;
  download_url: string;
  share_token: string;
  expires_at: string;
  warnings: string[];
}

export interface SharePage {
  title: string;
  client: string;
  summary: string;
  pain_points: string[];
  pilot: string | null;
  expires_at: string;
  video_url: string | null;
  deck_url: string | null;
}

export interface SettingsData {
  gateway: { base_url: string; fast_model: string; smart_model: string; polish_model: string; api_key_set: boolean };
  github: { mode: "mock" | "live"; token_set: boolean; private_default: true };
  budget: { run_limit_usd: number; monthly_cap_usd: number; hours_saved_per_run: number };
  retention_days: number;
}

/** The fields the form may change. There is no key or token field on purpose. */
export interface SettingsPatch {
  gateway?: { base_url?: string; fast_model?: string; smart_model?: string; polish_model?: string };
  budget?: { run_limit_usd?: number; monthly_cap_usd?: number; hours_saved_per_run?: number };
  retention_days?: number;
}

export interface GatewayTest {
  ok: boolean;
  models: string[];
  error: string | null;
}

export interface TemplateStat {
  sector: string;
  app_class: string;
  accent: string;
  screens: number;
  runs_used: number;
  builds_counted: number;
  first_time_ok: number;
  first_time_build_rate: number | null;
}

async function call<T>(path: string, init?: RequestInit): Promise<T> {
  let res: Response;
  try {
    res = await fetch(`${BASE_URL}${path}`, { cache: "no-store", ...init });
  } catch {
    throw new ApiError("The PoC Studio API is not reachable.");
  }
  if (!res.ok) {
    let detail: unknown;
    try {
      detail = ((await res.json()) as { detail?: unknown }).detail;
    } catch {
      detail = undefined;
    }
    throw new ApiError(typeof detail === "string" ? detail : `The API answered ${res.status}.`, res.status);
  }
  return (await res.json()) as T;
}

const send = (method: string, body?: unknown): RequestInit => ({
  method,
  headers: { "Content-Type": "application/json" },
  body: body === undefined ? undefined : JSON.stringify(body),
});

export const shareApi = {
  page: (token: string) => call<SharePage>(`/api/share/t/${encodeURIComponent(token)}`),
  createToken: (runId: string) => call<ShareToken>(`/api/share/${runId}`, send("POST")),
  exportZip: (runId: string) => call<ShareExport>(`/api/runs/${runId}/share-export`, send("POST")),
  downloadUrl: (runId: string) => `${BASE_URL}/api/runs/${runId}/share-export/download`,
  asset: (path: string) => `${BASE_URL}${path}`,
};

export const settingsApi = {
  get: () => call<SettingsData>("/api/settings"),
  put: (patch: SettingsPatch) => call<SettingsData>("/api/settings", send("PUT", patch)),
  testGateway: () => call<GatewayTest>("/api/settings/test-gateway", send("POST")),
};

export const templatesApi = {
  list: () => call<TemplateStat[]>("/api/templates"),
};

/** The page a client token opens on this machine: the web origin plus `/share/<token>`. */
export function shareLink(origin: string, path: string): string {
  return `${origin.replace(/\/$/, "")}${path}`;
}

export function formatExpiry(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime())
    ? ""
    : d.toLocaleDateString("en-GB", { day: "numeric", month: "long", year: "numeric" });
}

/** "9 of 10", or an em-dash-free "No builds yet". */
export function buildRateLabel(t: TemplateStat): string {
  return t.builds_counted === 0 ? "No builds yet" : `${t.first_time_ok} of ${t.builds_counted}`;
}
