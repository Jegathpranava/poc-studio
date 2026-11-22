import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { SettingsForm, buildPatch } from "@/components/settings/settings-form";
import { ShareActions } from "@/components/share/share-actions";
import { ShareView } from "@/components/share/share-view";

const notify = vi.hoisted(() => ({ success: vi.fn(), error: vi.fn(), info: vi.fn() }));
vi.mock("@/components/shell/notify", () => ({ notify }));

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

const page = {
  title: "Dispatch copilot",
  client: "Kestrel Freight Co.",
  summary: "A working proof of concept.",
  pain_points: ["Dispatchers match loads by phone."],
  pilot: "Pilot: 4 weeks, about $186 a month to run.",
  expires_at: "2026-12-22T10:00:00Z",
  video_url: "/api/share/t/tok/video",
  deck_url: "/api/share/t/tok/deck.html",
};

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

describe("share page", () => {
  it("shows the client view and links nowhere inside the app", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json(page)));
    const { container } = render(<ShareView token="tok" />);
    expect(await screen.findByRole("heading", { name: "Dispatch copilot" })).toBeTruthy();
    expect(container.querySelector("video")).not.toBeNull();
    expect(screen.getByText("What we heard")).toBeTruthy();
    expect(screen.getByText(/Pilot: 4 weeks/)).toBeTruthy();
    expect(screen.getByText(/expires on 22 December 2026/)).toBeTruthy();
    const deck = screen.getByRole("link", { name: /Open the interactive deck/ });
    expect(deck.getAttribute("target")).toBe("_blank");
    expect(deck.getAttribute("href")).toContain("/api/share/t/tok/deck.html");
    for (const a of Array.from(container.querySelectorAll("a"))) {
      expect(a.getAttribute("href") ?? "").not.toMatch(/^\/?(runs|settings|templates)\b/);
    }
    expect(container.textContent).not.toMatch(/Settings|Templates/);
  });

  it("explains an expired or bad link", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json({ detail: "This link has expired or is not valid" }, 404)));
    render(<ShareView token="bad" />);
    expect(await screen.findByText("This link has expired or is not valid")).toBeTruthy();
  });

  it("has a loading state", () => {
    vi.stubGlobal("fetch", vi.fn(() => new Promise<Response>(() => {})));
    render(<ShareView token="tok" />);
    expect(screen.getByLabelText("Loading")).toBeTruthy();
  });
});

describe("settings", () => {
  const settings = {
    gateway: { base_url: "https://gateway.example/v1", fast_model: "fast", smart_model: "smart", polish_model: "claude-haiku-5-5", api_key_set: true },
    github: { mode: "mock", token_set: false, private_default: true },
    budget: { run_limit_usd: 0.05, monthly_cap_usd: 5, hours_saved_per_run: 5.5 },
    retention_days: 30,
  };

  it("shows only whether a key is set, never a value", async () => {
    vi.stubGlobal("fetch", vi.fn(async () => json(settings)));
    const { container } = render(<SettingsForm />);
    expect(await screen.findByText("OPENAI_API_KEY is set in .env")).toBeTruthy();
    expect(screen.getByText("GITHUB_TOKEN is not set in .env")).toBeTruthy();
    expect(container.querySelectorAll('input[type="password"]').length).toBe(0);
    expect(Array.from(container.querySelectorAll("input")).some((i) => /^(sk-|ghp_)/.test(i.value))).toBe(false);
  });

  it("saves with a toast and tests the gateway", async () => {
    const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
      if (url.endsWith("/test-gateway")) return json({ ok: true, models: ["fast", "smart"], error: null });
      if (init?.method === "PUT") return json(settings);
      return json(settings);
    });
    vi.stubGlobal("fetch", fetchMock);
    render(<SettingsForm />);
    fireEvent.click(await screen.findByRole("button", { name: "Save settings" }));
    await waitFor(() => expect(notify.success).toHaveBeenCalledWith("Settings saved"));
    const put = fetchMock.mock.calls.find(([, init]) => init?.method === "PUT");
    expect(JSON.parse(String(put?.[1]?.body))).not.toHaveProperty("api_key");
    fireEvent.click(screen.getByRole("button", { name: "Test" }));
    await waitFor(() => expect(notify.success).toHaveBeenCalledWith("Gateway connected", "fast, smart"));
  });

  it("refuses a bad amount without calling the API", () => {
    const base = {
      base_url: "https://x.test/v1", fast_model: "fast", smart_model: "smart", polish_model: "p",
      run_limit_usd: "0", monthly_cap_usd: "5", hours_saved_per_run: "5.5", retention_days: "30",
    };
    expect(buildPatch(base)).toMatchObject({ field: "run_limit_usd" });
    expect(buildPatch({ ...base, run_limit_usd: "0.08" })).toHaveProperty("patch");
  });
});

describe("share actions", () => {
  it("copies the local token link and says it works on this machine only", async () => {
    const writeText = vi.fn(async () => {});
    vi.stubGlobal("navigator", { clipboard: { writeText } });
    vi.stubGlobal(
      "fetch",
      vi.fn(async () => json({ token: "abc123", path: "/share/abc123", expires_at: "2026-12-22T10:00:00Z" })),
    );
    render(<ShareActions runId="r_aaaaaa" />);
    expect(screen.getByRole("button", { name: "Download share zip" })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Copy client share link" }));
    await waitFor(() => expect(writeText).toHaveBeenCalledWith(`${window.location.origin}/share/abc123`));
    expect(notify.success).toHaveBeenCalledWith(
      "Link copied",
      "This link works on this machine only. Send the zip to the client.",
    );
  });
});
