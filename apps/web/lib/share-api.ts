import { ApiError, BASE_URL } from "./api";
import type { components } from "./api-types";

// Fetch helpers for sharing, settings and templates. They live here because api.ts belongs to the run pages.

type Schemas = components["schemas"];

export type ShareToken = Schemas["ShareTokenOut"];
export type ShareExport = Schemas["ShareExportOut"];
export type SharePage = Schemas["SharePageOut"];
export type SettingsData = Schemas["SettingsOut"];
/** The fields the form may change. There is no key or token field on purpose. */
export type SettingsPatch = Schemas["SettingsPatch"];
export type GatewayTest = Schemas["GatewayTest"];
export type TemplateStat = Schemas["TemplateStat"];

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
  body: JSON.stringify(body ?? {}), // the API guard needs a JSON body on every unsafe request
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
