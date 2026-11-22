import type { ActionItem, Constraint, Feature, Requirements } from "./requirements";

/** Editable view of a brief. `toRequirements` turns it back into the JSON the API validates. */
export interface BriefForm {
  title: string;
  goals: string;
  painPoints: string;
  budgetText: string;
  budgetAmount: string;
  timeline: string;
  constraints: Constraint[];
  features: Feature[];
  actionItems: { item: ActionItem; include: boolean }[];
}

const lines = (text: string): string[] =>
  text
    .split("\n")
    .map((l) => l.trim())
    .filter(Boolean);

const orNull = (text: string): string | null => (text.trim() ? text.trim() : null);

export function fromRequirements(req: Requirements): BriefForm {
  return {
    title: req.title,
    goals: req.goals.join("\n"),
    painPoints: req.pain_points.join("\n"),
    budgetText: req.budget.text ?? "",
    budgetAmount: req.budget.amount_usd === null ? "" : String(req.budget.amount_usd),
    timeline: req.timeline ?? "",
    constraints: req.constraints.map((c) => ({ ...c })),
    features: req.features.map((f) => ({ ...f })),
    actionItems: req.action_items.map((item) => ({ item: { ...item }, include: true })),
  };
}

export function toRequirements(base: Requirements, form: BriefForm): Requirements {
  const amount = Number(form.budgetAmount.replace(/[$,\s]/g, ""));
  return {
    ...base,
    title: form.title.trim() || base.title,
    goals: lines(form.goals),
    pain_points: lines(form.painPoints),
    budget: {
      text: orNull(form.budgetText),
      amount_usd: form.budgetAmount.trim() && Number.isFinite(amount) ? amount : null,
    },
    timeline: orNull(form.timeline),
    constraints: form.constraints.filter((c) => c.text.trim()).map((c) => ({ ...c, text: c.text.trim() })),
    features: form.features.map((f) => ({ ...f, name: f.name.trim(), detail: f.detail.trim() })),
    action_items: form.actionItems.filter((a) => a.include).map((a) => a.item),
  };
}

/** Problems the form can catch before the API does. */
export function validateForm(form: BriefForm): string[] {
  const problems: string[] = [];
  if (form.features.length === 0) problems.push("Keep at least one feature.");
  if (form.features.some((f) => !f.name.trim())) problems.push("Every feature needs a name.");
  if (form.budgetAmount.trim() && !Number.isFinite(Number(form.budgetAmount.replace(/[$,\s]/g, "")))) {
    problems.push("The budget amount must be a number.");
  }
  return problems;
}

export function newFeature(): Feature {
  return {
    name: "",
    detail: "",
    priority: "P2",
    confidence: 1,
    source_ts: null,
    source_quote: "Added in review",
  };
}

export function unconfirmedCount(form: BriefForm): number {
  return form.constraints.filter((c) => !c.confirmed).length;
}
