/** The `Requirements` contract from services/api/poc_studio/schemas/requirements.py. */
export type Sector = "logistics" | "healthcare" | "e-commerce" | "fintech" | "other";
export type Priority = "P1" | "P2" | "P3";

export interface Feature {
  name: string;
  detail: string;
  priority: Priority;
  confidence: number;
  source_ts: string | null;
  source_quote: string;
}

export interface Constraint {
  text: string;
  confirmed: boolean;
  source_quote: string | null;
}

export interface Budget {
  text: string | null;
  amount_usd: number | null;
}

export interface Stakeholder {
  name: string;
  role: string;
}

export interface ActionItem {
  text: string;
  owner: string | null;
  due: string | null;
}

export interface Requirements {
  client: string;
  sector: Sector;
  title: string;
  summary: string;
  goals: string[];
  pain_points: string[];
  features: Feature[];
  constraints: Constraint[];
  budget: Budget;
  timeline: string | null;
  stakeholders: Stakeholder[];
  action_items: ActionItem[];
}
