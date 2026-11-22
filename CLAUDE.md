# PoC Studio — Developer Guidelines & Architecture Rules

A local, single-user developer tool that turns a meeting transcript, BRD, TRD or any requirements doc into a scoped AI spec, a sector Next.js prototype, a GitHub repo, a pitch deck, a prototype walkthrough video and docs, in under 5 minutes of agent time.

## Start here
- Requirements: `docs/requirements/original-brief.md` (verbatim brief), `technical-solution-proposal.txt`, `problem-statement.txt`, `owner-direction-2026-11-22.md`.
- Intake decisions: `docs/intake/answers.json` (budget, single-user scope; overrides the proposal where they differ).
- Design spec and amendments: `docs/specs/` (written after the UI sample is approved). The spec wins over the brief.
- Visual reference (APPROVED 2026-11-22, 2 rounds): `design/preview/preview.html` (sources in `design/preview/src/`), tokens frozen in `design/preview/tokens.css`. Approval record with sha256: `docs/intake/approval.json`.
- Cloud sessions: read `docs/handoff/` first (not prepared; cloud handoff is "maybe").

## Mission
Transcript or requirements doc -> requirements.json + action items -> architecture.md (Mermaid, model picks, cost table) -> Next.js sector prototype (build-validated) -> Reveal.js deck + Playwright walkthrough video + docs -> QA -> GitHub repo on the owner's account.

## Core tech stack (budget build, decided at intake)
- Backend: Python 3.12, FastAPI, Pydantic v2, SSE. LangGraph supervisor with `interrupt()` for the two gates and a SQLite checkpointer; runs are asyncio tasks in the API process (no Redis/Celery).
- Data: SQLite (projects, runs, agent_steps, artifacts, approvals) + versioned files under `runs/<id>/`. Postgres later by changing `DATABASE_URL`.
- Frontend: Next.js 16 (App Router), Tailwind CSS, shadcn/ui, Lucide icons, sileo toasts.
- LLM gateway: https://gateway.ai.skyformit.com/v1 (OpenAI compatible)
  - Bulk extraction and code gen: `fast` / `smart` (Ollama, free)
  - Executive pitch deck polish: `claude-haiku-5-5` (only paid call; budget target under $0.05 per run)
- Prototype sandbox: local Docker container per run when Docker exists; plain folder fallback (Docker is not installed on this machine yet).
- Deck: Reveal.js + python-pptx export. Video: Playwright headless recording.
- GitHub: fine-grained personal token on `Jegathpranava`, REST. Generated client repos default to private.

## 7 agents
- Orchestrator (0): LangGraph supervisor, event stream, 2 approval gates, retries, per-run budget stop.
- Meeting Intelligence (1): transcript/doc -> goals, ranked features, constraints, budget, timeline, sector, stakeholders, action items -> `requirements.json`.
- Solution Architect (2): requirements -> use-case class, model picks, data flow, Mermaid, monthly cost -> `architecture.md`.
- Prototype Builder (3): sector template (healthcare, logistics, e-commerce, fintech) -> pages, forms, mock data, API stubs -> `npm run build`, fix loop max 3.
- Repo & DevOps (4): repo, README, `.env.example`, CI workflow, push, issues from action items.
- Pitch & Docs (5): 8-10 slide deck, executive summary, user flows, walkthrough video.
- QA Reviewer (6): cross-artifact consistency, build passed, secret scan, link check; failures go back to the owner agent at most twice.

## Human approval gates
- Gate 1 (post-requirements): developer edits/approves `requirements.json` before code generation.
- Gate 2 (pre-publish): developer previews prototype, deck and video before anything is pushed to GitHub.

## Rules
- Never print, log, commit or paste secrets. `.env*` except `.env.example` is git-ignored; never overwrite the owner's `.env`.
- Tests never hit the real gateway or GitHub: `LLM_PROVIDER=mock`, `GITHUB_MODE=mock`. Mocks are refused when `APP_ENV=production`.
- LLM calls: schema in the prompt, Pydantic-validated output, retry on invalid JSON, tokens and cost logged per step.
- Clean, modular, typed code. No monolith files: agents, routes and UI components stay in separate modules. Avoid unnecessary dependencies.
- Toasts use `sileo`. Icons use Lucide. No emojis in the UI.
- Read the current Next.js 16 and LangGraph docs (context7) before using their APIs.

## Commands
- To be filled in by the first build increment (install, dev servers on web :3000 / API :8000, typecheck, tests).
