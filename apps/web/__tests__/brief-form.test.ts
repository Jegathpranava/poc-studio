import { describe, expect, it } from "vitest";

import { fromRequirements, newFeature, toRequirements, unconfirmedCount, validateForm } from "@/lib/brief-form";
import type { Requirements } from "@/lib/requirements";

const BASE: Requirements = {
  client: "Kestrel Freight Co.",
  sector: "logistics",
  title: "Dispatch copilot",
  summary: "A summary.",
  goals: ["Cut dispatch time", "Fewer empty miles"],
  pain_points: ["Manual routing"],
  features: [
    { name: "Route suggestions", detail: "Ranked", priority: "P1", confidence: 0.9, source_ts: "00:01:02", source_quote: "we route by hand" },
  ],
  constraints: [
    { text: "Data stays in the US", confirmed: false, source_quote: null },
    { text: "Pilot by March", confirmed: true, source_quote: "by March" },
  ],
  budget: { text: "About $40k", amount_usd: 40000 },
  timeline: "March",
  stakeholders: [{ name: "Ana", role: "COO" }],
  action_items: [
    { text: "Send the sample", owner: "Ana", due: "Fri" },
    { text: "Book a follow-up", owner: null, due: null },
  ],
};

describe("brief form", () => {
  it("round-trips an untouched brief to the same JSON", () => {
    expect(toRequirements(BASE, fromRequirements(BASE))).toEqual(BASE);
  });

  it("turns edited fields into JSON", () => {
    const form = fromRequirements(BASE);
    form.budgetText = "About $55k";
    form.budgetAmount = "$55,000";
    form.goals = "Cut dispatch time\n\n  Win back drivers  \n";
    form.timeline = "";
    form.features[0].priority = "P2";
    const out = toRequirements(BASE, form);
    expect(out.budget).toEqual({ text: "About $55k", amount_usd: 55000 });
    expect(out.goals).toEqual(["Cut dispatch time", "Win back drivers"]);
    expect(out.timeline).toBeNull();
    expect(out.features[0].priority).toBe("P2");
    expect(out.client).toBe(BASE.client); // fields without a control are kept
  });

  it("drops unchecked action items and blank constraints", () => {
    const form = fromRequirements(BASE);
    form.actionItems[1].include = false;
    form.constraints[0].text = "   ";
    const out = toRequirements(BASE, form);
    expect(out.action_items).toEqual([BASE.action_items[0]]);
    expect(out.constraints).toEqual([BASE.constraints[1]]);
  });

  it("counts unconfirmed constraints and flags problems before the API does", () => {
    const form = fromRequirements(BASE);
    expect(unconfirmedCount(form)).toBe(1);
    expect(validateForm(form)).toEqual([]);
    form.features = [...form.features, newFeature()];
    form.budgetAmount = "lots";
    expect(validateForm(form)).toEqual(["Every feature needs a name.", "The budget amount must be a number."]);
    form.features = [];
    expect(validateForm(form)).toContain("Keep at least one feature.");
  });
});
