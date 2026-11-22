# PoC Studio — Developer Guidelines & Architecture Rules

## Mission
Build "PoC Studio" (Meeting-to-PoC Platform): a developer tool that turns raw meeting transcripts into a scoped AI spec, Next.js sector prototype, GitHub repository, and client pitch deck under 5 minutes.

## Core Tech Stack
- Backend: Python 3.11+, FastAPI, LangGraph (state graph supervisor), SQLite/PostgreSQL, SSE for streaming.
- Frontend: Next.js 14 (App Router), Tailwind CSS, Lucide icons, shadcn/ui.
- Agent LLM Gateway: https://gateway.ai.skyformit.com/v1 (OpenAI compatible)
  - Bulk Extraction & Code Gen: `fast` / `smart` (Ollama - Free)
  - Executive Pitch Deck Polish: `claude-haiku-5-5` (budget-conscious)

## 6 Specialist Agents & State
- Orchestrator (0): LangGraph supervisor controlling execution, event streams, and 2 human approval gates.
- Meeting Intelligence (1): Ingests transcript -> extracts goals, pain points, features, sector, budget -> outputs `requirements.json`.
- Solution Architect (2): Ingests `requirements.json` -> designs AI pipeline, Mermaid diagram, model picks, cost table -> outputs `architecture.md`.
- Prototype Builder (3): Ingests requirements + architecture -> selects sector template -> generates Next.js pages & mock APIs -> runs build validation loop.
- Repo & DevOps (4): Git automation -> creates GitHub repo via API, README, CI workflow, pushes code.
- Pitch & Docs (5): Ingests specs -> outputs 8-10 slide web pitch deck (Reveal.js) & executive summary.
- QA Reviewer (6): Validates schema alignment, checks for leaked secrets, ensures build passes.

## Human Approval Gates
- Gate 1 (Post-Requirements): Halts for developer to review/edit `requirements.json` before code generation.
- Gate 2 (Pre-Publish): Halts for developer to preview web prototype and slide deck before pushing to GitHub.

## Coding Style & Budget Rules
- Write clean, modular, production-ready code with type annotations and Pydantic v2 schemas.
- Do NOT generate massive monolithic files; keep agents, routes, and UI components cleanly separated.
- Avoid unnecessary external dependencies.