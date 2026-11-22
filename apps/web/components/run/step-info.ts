import {
  Code,
  FileText,
  Film,
  GitBranch,
  Hammer,
  LayoutTemplate,
  Presentation,
  ShieldCheck,
  Sparkles,
  Workflow,
  type LucideIcon,
} from "lucide-react";

import type { StepRow } from "@/lib/run-steps";

export interface StepInfo {
  title: string;
  /** Shown while the step has not started. */
  waiting: string;
  icon: LucideIcon;
  tag?: string;
}

export const STEP_INFO: Record<string, StepInfo> = {
  intake: { title: "Intake", waiting: "Parses the uploaded files", icon: FileText },
  intelligence: { title: "Meeting Intelligence", waiting: "Extracts the brief from the transcript", icon: Sparkles },
  architect: { title: "Solution Architect", waiting: "Waits for the approved brief", icon: Workflow },
  screens: { title: "Prototype Builder: screens", waiting: "Waits for the architecture", icon: LayoutTemplate },
  pitch: { title: "Pitch and Docs", waiting: "Waits for the screens", icon: Presentation, tag: "in parallel" },
  port: { title: "Prototype Builder: Next.js app", waiting: "Waits for the screens", icon: Code, tag: "in parallel" },
  assemble: { title: "Deck assembly", waiting: "Waits for the pitch and the app", icon: Hammer },
  qa: { title: "QA Reviewer", waiting: "Waits for the prototype and deck", icon: ShieldCheck },
  video: { title: "Walkthrough video", waiting: "Recorded after you approve at Gate 2", icon: Film },
  repo: { title: "Repo and DevOps", waiting: "Creates the GitHub repo after your approval", icon: GitBranch },
};

export function stepInfo(agent: string): StepInfo {
  return STEP_INFO[agent] ?? { title: agent, waiting: "Waiting", icon: Workflow };
}

/** The most recent real log line, without the automatic start and finish markers. */
export function stepSummary(row: StepRow, fallback: string): string {
  for (let i = row.logs.length - 1; i >= 0; i--) {
    const line = row.logs[i];
    if (line.tone === "plain" && !line.text.startsWith("started,")) return line.text;
  }
  return fallback;
}
