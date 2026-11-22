import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { BudgetBanner, RunBudgetBanner } from "@/components/run/budget-banner";
import { RequestChanges } from "@/components/run/request-changes";
import { ReviseButton } from "@/components/run/revise-button";
import { StepActions } from "@/components/run/step-actions";
import { raiseTarget, retryKind } from "@/lib/revise";

const run = vi.hoisted(() => ({
  value: { runId: "r_aaaaaa", status: "waiting_gate2", detail: { budget_usd: 0.05 }, reload: () => {} } as Record<string, unknown>,
}));
const nav = vi.hoisted(() => ({ push: vi.fn() }));
const toast = vi.hoisted(() => ({ success: vi.fn(), info: vi.fn(), error: vi.fn() }));
vi.mock("@/components/run/run-context", () => ({ useRun: () => run.value }));
vi.mock("next/navigation", () => ({ useRouter: () => ({ push: nav.push }) }));
vi.mock("@/components/shell/notify", () => ({ notify: toast }));

const json = (body: unknown, status = 200) => new Response(JSON.stringify(body), { status });
const calls = () => (fetch as unknown as ReturnType<typeof vi.fn>).mock.calls as [string, RequestInit][];

beforeEach(() => {
  run.value = { runId: "r_aaaaaa", status: "waiting_gate2", detail: { budget_usd: 0.05 }, reload: vi.fn() };
  vi.stubGlobal("fetch", vi.fn(() => Promise.resolve(json({ run_id: "r_aaaaaa", status: "running" }))));
});
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.clearAllMocks();
});

describe("RequestChanges onSend", () => {
  it("hands over the trimmed note, and Send stays disabled while the note is empty", () => {
    const onSend = vi.fn();
    render(<RequestChanges open title="Request changes" onCancel={() => {}} onSend={onSend} />);
    const send = screen.getByRole("button", { name: "Send" }) as HTMLButtonElement;
    expect(send.disabled).toBe(true);
    fireEvent.change(screen.getByLabelText("Note"), { target: { value: "  Shorter deck  " } });
    fireEvent.click(send);
    expect(onSend).toHaveBeenCalledWith("Shorter deck");
  });
});

describe("Request changes button", () => {
  it("posts the note to the revise endpoint, toasts who reruns and goes to the timeline", async () => {
    render(<ReviseButton type="deck" />);
    fireEvent.click(screen.getByRole("button", { name: "Request changes" }));
    fireEvent.change(screen.getByLabelText("Note"), { target: { value: "Lead with the saving" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    await waitFor(() => expect(nav.push).toHaveBeenCalledWith("/runs/r_aaaaaa"));
    const [url, init] = calls()[0];
    expect(url).toMatch(/\/api\/runs\/r_aaaaaa\/artifacts\/deck\/revise$/);
    expect(JSON.parse(String(init.body))).toEqual({ note: "Lead with the saving" });
    expect(toast.success).toHaveBeenCalledWith("Change request sent", "Only Pitch and Docs reruns. About 2 minutes.");
  });

  it("is disabled unless the run waits at Gate 2", () => {
    run.value = { ...run.value, status: "running" };
    render(<ReviseButton type="architecture" />);
    expect((screen.getByRole("button", { name: "Request changes" }) as HTMLButtonElement).disabled).toBe(true);
  });

  it("shows the API error in the dialog and stays open", async () => {
    vi.stubGlobal("fetch", vi.fn(() => Promise.resolve(json({ detail: "run is running, not waiting at gate publish" }, 409))));
    render(<ReviseButton type="prototype" />);
    fireEvent.click(screen.getByRole("button", { name: "Request changes" }));
    fireEvent.change(screen.getByLabelText("Note"), { target: { value: "More screens" } });
    fireEvent.click(screen.getByRole("button", { name: "Send" }));
    expect(await screen.findByText("run is running, not waiting at gate publish")).toBeTruthy();
    expect(nav.push).not.toHaveBeenCalled();
  });
});

describe("retry buttons", () => {
  it("appear only for a failed port at Gate 2 or a failed run", () => {
    expect(retryKind("port", true, "waiting_gate2")).toBe("port");
    expect(retryKind("pitch", true, "waiting_gate2")).toBeNull();
    expect(retryKind("port", false, "waiting_gate2")).toBeNull();
    expect(retryKind("port", true, "running")).toBeNull();
    expect(retryKind("architect", true, "failed")).toBe("resume");
    expect(retryKind("architect", false, "failed")).toBeNull();
    expect(retryKind("port", true, "delivered")).toBeNull();
  });

  it("a failed port offers 3 more attempts and a note, and 3 more attempts posts attempts 3", async () => {
    render(<StepActions agent="port" failed runId="r_aaaaaa" status="waiting_gate2" />);
    expect(screen.getByRole("button", { name: /Retry with a note/ })).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: /Retry with 3 more attempts/ }));
    await waitFor(() => expect(toast.info).toHaveBeenCalledWith("Retrying the build", "Prototype Builder gets 3 more fix attempts."));
    const [url, init] = calls()[0];
    expect(url).toMatch(/\/api\/runs\/r_aaaaaa\/retry$/);
    expect(JSON.parse(String(init.body))).toEqual({ attempts: 3 });
  });

  it("retry with a note sends the note", async () => {
    render(<StepActions agent="port" failed runId="r_aaaaaa" status="waiting_gate2" />);
    fireEvent.click(screen.getByRole("button", { name: /Retry with a note/ }));
    fireEvent.change(screen.getByLabelText("Note"), { target: { value: "use usePlans" } });
    fireEvent.click(screen.getByRole("button", { name: "Retry" }));
    await waitFor(() => expect(calls()).toHaveLength(1));
    expect(JSON.parse(String(calls()[0][1].body))).toEqual({ note: "use usePlans", attempts: 3 });
  });

  it("a failed run offers Resume only", async () => {
    render(<StepActions agent="architect" failed runId="r_aaaaaa" status="failed" />);
    expect(screen.queryByRole("button", { name: /Retry with/ })).toBeNull();
    fireEvent.click(screen.getByRole("button", { name: "Resume" }));
    await waitFor(() => expect(calls()).toHaveLength(1));
    expect(JSON.parse(String(calls()[0][1].body))).toEqual({});
  });

  it("renders nothing for other steps", () => {
    const { container } = render(<StepActions agent="pitch" failed runId="r_aaaaaa" status="waiting_gate2" />);
    expect(container.innerHTML).toBe("");
  });
});

describe("budget banner", () => {
  it("names the limit, offers double and the free model", () => {
    const onRaise = vi.fn();
    const onFree = vi.fn();
    render(<BudgetBanner limitUsd={0.05} onRaise={onRaise} onFreeModel={onFree} />);
    expect(screen.getByText("Paused: this run reached its $0.05 paid limit.")).toBeTruthy();
    fireEvent.click(screen.getByRole("button", { name: "Raise to $0.10 for this run" }));
    expect(onRaise).toHaveBeenCalledWith(0.1);
    fireEvent.click(screen.getByRole("button", { name: "Use the free model" }));
    expect(onFree).toHaveBeenCalledTimes(1);
  });

  it("caps the raise at $1.00 and hides it when there is no room", () => {
    expect(raiseTarget(0.8)).toBe(1);
    expect(raiseTarget(1)).toBeNull();
    render(<BudgetBanner limitUsd={1} onRaise={() => {}} onFreeModel={() => {}} />);
    expect(screen.queryByRole("button", { name: /Raise to/ })).toBeNull();
    expect(screen.getByRole("button", { name: "Use the free model" })).toBeTruthy();
  });

  it("only shows while the run is paused on its budget", () => {
    const { container } = render(<RunBudgetBanner />);
    expect(container.innerHTML).toBe("");
    cleanup();
    run.value = { ...run.value, status: "paused_budget" };
    render(<RunBudgetBanner />);
    expect(screen.getByTestId("budget-banner")).toBeTruthy();
  });

  it("raising posts the new budget and toasts; the free model posts use_free_model", async () => {
    run.value = { ...run.value, status: "paused_budget" };
    render(<RunBudgetBanner />);
    fireEvent.click(screen.getByRole("button", { name: "Raise to $0.10 for this run" }));
    await waitFor(() => expect(toast.success).toHaveBeenCalledWith("Budget raised to $0.10 for this run", "Pitch and Docs continues."));
    expect(calls()[0][0]).toMatch(/\/api\/runs\/r_aaaaaa\/budget$/);
    expect(JSON.parse(String(calls()[0][1].body))).toEqual({ budget_usd: 0.1 });
    fireEvent.click(screen.getByRole("button", { name: "Use the free model" }));
    await waitFor(() => expect(calls()).toHaveLength(2));
    expect(JSON.parse(String(calls()[1][1].body))).toEqual({ use_free_model: true });
  });
});
