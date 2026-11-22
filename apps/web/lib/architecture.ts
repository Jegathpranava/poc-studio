/** The `Architecture` contract from services/api/poc_studio/schemas/architecture.py. */
export type UseCaseClass = "rag" | "agent" | "classifier" | "vision" | "forecasting" | "other";

export interface Component {
  name: string;
  kind: string;
  detail: string;
}

export interface ModelPick {
  job: string;
  model: string;
  cost_per_1k_calls_usd: number;
}

export interface CostLine {
  item: string;
  usd: number;
}

export interface MonthlyCost {
  lines: CostLine[];
  total_usd: number;
  assumptions: string;
}

export interface Phase {
  name: string;
  weeks: number;
  detail: string;
}

export interface Architecture {
  use_case_class: UseCaseClass;
  components: Component[];
  mermaid: string;
  models: ModelPick[];
  monthly_cost: MonthlyCost;
  phases: Phase[];
  rationale: string;
}

const USE_CASE_LABELS: Record<UseCaseClass, string> = {
  rag: "Retrieval (RAG)",
  agent: "Agent",
  classifier: "Classifier",
  vision: "Vision",
  forecasting: "Forecasting",
  other: "Custom pipeline",
};

export const labelForUseCase = (c: UseCaseClass): string => USE_CASE_LABELS[c] ?? c;

export const usd = (n: number): string =>
  `$${n.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
