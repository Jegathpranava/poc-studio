# PoC Studio — Developer Guidelines & Architecture Rules

A local, single-user developer tool that turns a meeting transcript, BRD, TRD or any requirements doc into a scoped AI spec, a sector Next.js prototype, a GitHub repo, a pitch deck, a prototype walkthrough video and docs, in under 5 minutes of agent time.

## Start here
- Requirements: `docs/requirements/original-brief.md` (verbatim brief), `technical-solution-proposal.txt`, `problem-statement.txt`, `owner-direction-2026-11-22.md`.
- Intake decisions: `docs/intake/answers.json` (budget, single-user scope; overrides the proposal where they differ).
- Design spec (AUTHORITY): `docs/specs/2026-11-22-poc-studio-design.md`. It wins over the brief and over this file where they differ; read sections 3, 7a and 7b before building.
- Visual reference (APPROVED 2026-11-22, 3 rounds; v3 adds the reference deck frame and MP4 player): `design/preview/preview.html` (sources in `design/preview/src/`), tokens frozen in `design/preview/tokens.css`. Approval record with sha256: `docs/intake/approval.json`.
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
- Deck: self-contained HTML deck in the owner reference format (1280x720 stage, template product frames, step spotlights); runtime vendored, assembled deterministically (spec 7a). `.pptx` as static export. Video: Playwright walkthrough of the deck, MP4 via imageio-ffmpeg; MP4 player on deck and share views.
- Owner reference material lives in `reference/` (git-ignored; this repo is public). Never commit it.
- GitHub: fine-grained personal token on `Jegathpranava`, REST. Generated client repos default to private.

## 7 agents
- Orchestrator (0): LangGraph supervisor, event stream, 2 approval gates, retries, per-run budget stop.
- Meeting Intelligence (1): transcript/doc -> goals, ranked features, constraints, budget, timeline, sector, stakeholders, action items -> `requirements.json`.
- Solution Architect (2): requirements -> use-case class, model picks, data flow, Mermaid, monthly cost -> `architecture.md`.
- Prototype Builder (3): sector kit -> ScreenPack (6-12 product screens as scoped HTML fragments with spotlight anchors) -> deck; then ported to a Next.js app for the repo -> `npm run build`, fix loop max 3.
- Repo & DevOps (4): repo, README, `.env.example`, CI workflow, push, issues from action items.
- Pitch & Docs (5): dk-data slide plan (welcome, overview tour, area slides with steps, play, close with sourced figures), executive summary, user flows, .pptx; walkthrough MP4 recorded after Gate 2.
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
- Install: `npm ci` (root, includes `apps/web`), then `cd services/api && uv sync`; database: `cd services/api && uv run alembic upgrade head` (SQLite at `data/poc-studio.sqlite`, override with `POC_DATABASE_URL`).
- Run: `npm run dev` starts the API on 127.0.0.1:8000 and the web app on 127.0.0.1:3000. Real models need `LLM_PROVIDER=gateway` in `.env`; default is `mock`. Publishing stays mocked until `GITHUB_MODE=live`.
- Checks: `npm run lint`, `npm run typecheck`, `npm test` (pytest without slow/live, plus Vitest). Browser: `cd services/api && uv run pytest -m browser`. Slow (real npm build): `uv run pytest -m slow`. E2E: `npm --workspace apps/web run e2e` (starts its own servers on mocks).
- API types after an API change: start the API, then `npm --workspace apps/web run gen:types`.
- KPI: `cd services/api && uv run python ../../eval/run_eval.py --stage full --dry` (pipeline only); live runs need `EVAL_LIVE=1` and the owner's yes (see `eval/README.md`).

## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- When graphify-out/graph.json exists, run `graphify query "<question>"` before your first grep, search or source-file read for a codebase question, and put this rule in every subagent prompt that explores code. Read raw files only for lines the graph or an earlier read already located. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).
- A committed graphify-out/graph.json is rewritten whole on every build, so a large diff to it in a pull request is expected. Do not flag it as churn or suggest skipping the graph rebuild or its hooks.

## Knowledge graph (graphify)
- The graph lives in `graphify-out/`. Read `graphify-out/GRAPH_REPORT.md` before searching the codebase. Ask it questions with `graphify query "<question>"`.
- After every release, starting with the first, update the graph and commit it with the release: run `graphify update .` (code only, no tokens). When docs, specs or images changed, also run `/graphify . --update`. Then run `git add graphify-out/GRAPH_REPORT.md graphify-out/graph.json`.
- The git hooks (`graphify hook install`) keep the code graph current between releases.
