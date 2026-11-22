import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import { DeviceFrame, DeviceToggle } from "@/components/prototype/device-frame";
import { PrototypeView } from "@/components/prototype/prototype-view";
import { useState } from "react";

vi.mock("@/components/run/run-context", () => ({ useRun: () => ({ runId: "r_aaaaaa", status: "waiting_gate2" }) }));
vi.mock("@/components/shell/notify", () => ({ notify: { info: vi.fn(), error: vi.fn(), success: vi.fn() } }));

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });

function routes(map: Record<string, () => Response>) {
  vi.stubGlobal(
    "fetch",
    vi.fn((url: string) => {
      const hit = Object.entries(map).find(([k]) => url.endsWith(k));
      return Promise.resolve(hit ? hit[1]() : json({ detail: "nope" }, 404));
    }),
  );
}

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
});

function Harness() {
  const [d, setD] = useState<"desktop" | "mobile">("desktop");
  return (
    <>
      <DeviceToggle value={d} onChange={setD} />
      <DeviceFrame device={d} url="http://127.0.0.1:4300/">
        <span />
      </DeviceFrame>
    </>
  );
}

describe("Prototype page", () => {
  it("the device toggle switches the frame class", () => {
    render(<Harness />);
    expect(screen.getByTestId("device").className).toBe("device");
    fireEvent.click(screen.getByRole("button", { name: "Phone" }));
    expect(screen.getByTestId("device").className).toBe("device mobile");
    expect(screen.getByRole("button", { name: "Phone" }).getAttribute("aria-pressed")).toBe("true");
    fireEvent.click(screen.getByRole("button", { name: "Desktop" }));
    expect(screen.getByTestId("device").className).toBe("device");
  });

  it.each([404, 409])("shows the not-built state when /build returns %i", async (status) => {
    routes({ "/build": () => json({ detail: "Prototype not built" }, status) });
    render(<PrototypeView />);
    expect(await screen.findByText("Available after the Prototype Builder runs")).toBeTruthy();
  });

  it("shows the structured error and no iframe when the build failed", async () => {
    routes({
      "/build": () =>
        json({
          ok: false,
          duration_s: 4.2,
          attempts: 3,
          error: { file: "app/page.tsx", line: 4, col: 1, message: "Module not found", excerpt: "> 4 | import X" },
          log_tail: "boom",
        }),
      "/files": () => json([]),
    });
    render(<PrototypeView />);
    expect(await screen.findByText("Retry arrives in a later step.")).toBeTruthy();
    expect(screen.getByText(/app\/page\.tsx:4:1/)).toBeTruthy();
    expect(screen.getByText("Build failed after 3 attempts")).toBeTruthy();
    expect(document.querySelector("iframe")).toBeNull();
  });

  it("starts the preview, frames it and offers Open in new tab", async () => {
    routes({
      "/build": () => json({ ok: true, duration_s: 9.1, attempts: 1, log_tail: "ok" }),
      "/files": () => json([{ name: "app", path: "app", type: "dir", children: [{ name: "page.tsx", path: "app/page.tsx", type: "file" }] }]),
      "/preview": () => json({ url: "http://127.0.0.1:4300/", port: 4300 }),
    });
    render(<PrototypeView />);
    await waitFor(() => expect(document.querySelector("iframe")?.getAttribute("src")).toBe("http://127.0.0.1:4300/"));
    expect(screen.getByRole("link", { name: /Open in new tab/ }).getAttribute("href")).toBe("http://127.0.0.1:4300/");
    expect(await screen.findByText("page.tsx")).toBeTruthy();
  });

  it("offers Try again when the preview cannot start", async () => {
    routes({
      "/build": () => json({ ok: true, duration_s: 9.1, attempts: 1 }),
      "/files": () => json([]),
      "/preview": () => json({ detail: "The preview server did not answer within 30 seconds" }, 502),
    });
    render(<PrototypeView />);
    expect(await screen.findByText("The preview could not start.")).toBeTruthy();
    expect(screen.getByRole("button", { name: /Try again/ })).toBeTruthy();
  });
});
