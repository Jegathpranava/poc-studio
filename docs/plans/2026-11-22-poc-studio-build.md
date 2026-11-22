# PoC Studio build plan

Spec: `docs/specs/2026-11-22-poc-studio-design.md`. It is the authority; read sections 3, 7, 7a and 7b first.
Visual reference: `design/preview/preview.html`, approved v3 (`docs/intake/approval.json`). Tokens: `design/preview/tokens.css`.
Goal: one transcript or requirements doc in; a brief, an architecture spec, a deck in the reference format, an MP4 walkthrough, a Next.js repo on GitHub and a share zip out. Under 5 minutes of agent time and under $0.05 of paid spend per run, with two approval gates.
Approach: seven increments, each runnable and visible. The API (FastAPI + LangGraph) and the web app (Next.js 16) live in one monorepo. Every external service has a mock switch, so the build and the tests never need keys.
Execution: subagent-driven, with reviews batched after tasks 1-3, 4-8, 9-13b, 14-16 and 17-21. A plan-critic pass runs against the spec at the end.

## Global constraints

**Runtimes and stack**
- Node 24, npm workspaces; Python 3.12, uv; Next.js 16 App Router, TypeScript strict, Tailwind v4; FastAPI, Pydantic v2, SQLAlchemy 2, Alembic, LangGraph with `AsyncSqliteSaver`.
- Web on 127.0.0.1:3000, API on 127.0.0.1:8000, prototype previews on ports 4300 to 4399. Bind to 127.0.0.1 only.
- Tokens: port the `:root` block of `design/preview/tokens.css` verbatim into `apps/web/app/tokens.css`, mapped to the Tailwind v4 `@theme`. No hex anywhere else in `apps/web` (check: `grep -rE "#[0-9a-fA-F]{3,8}\b" apps/web --include=*.tsx`).
- Libraries: icons are `lucide-react`; toasts are `sileo`, mounted once, and sonner, react-hot-toast and react-toastify are banned. No emojis. No native `<select>`: comboboxes are custom with an inline "create". Copy is in sentence case.

**LLMs**
- Models: `DEFAULT_FAST_MODEL` (`fast`), `DEFAULT_SMART_MODEL` (`smart`), `POLISH_MODEL` (`claude-haiku-5-5`), all through `OPENAI_BASE_URL`. Never hardcode keys.
- Every LLM output is validated against a Pydantic schema, with 2 repair retries and a 90 s timeout per call. Tokens, cost and model are logged on each `agent_steps` row.

**Tests and mocks**
- Tests never hit the real gateway, GitHub or npm registry, except tests marked `slow` (npm) and `live` (opt-in through env vars).
- `LLM_PROVIDER=mock` and `GITHUB_MODE=mock` are the test defaults, and are refused when `APP_ENV=production`.

**Secrets and git**
- Never print, log or commit secrets. Never overwrite `.env`; add new variable names to `.env.example`.
- `reference/` and `runs/` stay git-ignored. Only the vendored deck engine (amendment 9) is committed.

**Code layout**
- One module per agent. No file over about 400 lines; split by responsibility.
- Each UI state (loading, empty, error) is built for every list and form, as in the preview.

**Commits**
- Commits go on `feat/<increment>` branches with the trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` and author email `jegathpranava@gmail.com`.
- Push after each verified task. Never push to main without the owner's merge.

- Dependencies: Task 1 installs the whole Python and JS dependency set listed in Task 1. A later task that needs a new package adds it in its own commit, and dependency edits are merged one after another, never in parallel (`pyproject.toml`, `uv.lock` and `package-lock.json` are shared files).
- Graph wiring: each agent module exposes `NODE = NodeSpec(name, fn, owner_agent)`, and `graph/registry.py` collects them. Agent tasks never edit `graph/build.py`. Wiring changes happen only in Task 6 (stubs) and Task 18b (the final wiring).
- Mock fixtures: each agent task owns `tests/fixtures/llm/<agent>.json`.
- Test markers: `slow` (npm network or a real build), `browser` (needs Playwright Chromium), `live` (real gateway or GitHub, opt-in through `EVAL_LIVE=1` or `GITHUB_MODE=live`). CI runs the default and `browser` markers after `playwright install --with-deps chromium`. It never runs `slow` or `live`.
- Resolved values (also recorded in `docs/decisions.md` by Task 1): run id `r_` plus 6 hex; deck 9 to 12 slides; build timeout 90 s, install 180 s; video 120 to 180 s with the hands-on slide skipped.

## File map

| Path | Responsibility | Task |
|---|---|---|
| `package.json`, `scripts/dev.mjs` | workspaces; `npm run dev` starts API and web together; `npm test` runs all | 1 |
| `services/api/pyproject.toml`, `poc_studio/main.py`, `config.py` | FastAPI app, settings from env, mock switches | 1 |
| `services/api/poc_studio/db/` (`models.py`, `session.py`), `alembic/` | the tables in spec section 7 and 7b, migrations | 1 |
| `services/api/poc_studio/routes/schemas.py` | request and response models (Task 1 writes every endpoint shape from spec 7 and 7b up front; later tasks only fill in handlers) | 1 |
| `services/api/poc_studio/schemas/` (`screenpack.py`, `deck.py`) | shared contracts from spec 7a and 7b, used by Tasks 11, 14 and 15 | 1 |
| `services/api/poc_studio/graph/registry.py` | node registry (`NodeSpec`) | 6 |
| `docs/decisions.md` | resolved values and verified prices | 1, appended by 4 |
| `apps/web/` (`app/layout.tsx`, `tokens.css`, `components/shell/*`) | app shell: rail, phone tab bar, toaster | 2 |
| `apps/web/lib/api.ts`, `lib/api-types.ts` | typed client; types generated from OpenAPI | 2 |
| `apps/web/app/page.tsx`, `components/runs/*` | Runs list with loading, empty and error states | 2 |
| `.github/workflows/ci.yml` | lint, typecheck, unit and integration tests (mocks) | 3 |
| `services/api/poc_studio/llm/` (`client.py`, `mock.py`, `pricing.py`, `budget.py`, `json_repair.py`) | gateway client, mock, pre-call budget guard, cost metering | 4 |
| `services/api/poc_studio/ingest/` (`parse.py`, `vtt.py`) | txt, vtt, md, docx and pdf to normalised text with timestamps | 5 |
| `eval/fixtures/*.vtt`, `*.md` | 10 fictional transcripts and BRDs across the 4 sectors | 5 |
| `services/api/poc_studio/graph/` (`state.py`, `build.py`, `nodes.py`), `events.py`, `runs/service.py` | LangGraph graph, gates through `interrupt()`, event bus, run lifecycle | 6 |
| `services/api/poc_studio/routes/runs.py`, `routes/events.py`, `routes/gates.py` | run CRUD, SSE, gate decisions | 6 |
| `services/api/poc_studio/agents/intelligence.py`, `schemas/requirements.py` | Meeting Intelligence agent | 7 |
| `apps/web/app/runs/new/*`, `app/runs/[id]/layout.tsx` (sub-nav), `app/runs/[id]/page.tsx` (timeline), `app/runs/[id]/brief/*`, `components/run/*` | New run, sticky sub-nav, timeline with collapsible logs, Gate 1 | 8 |
| `services/api/poc_studio/agents/architect.py`, `schemas/architecture.py`; `apps/web/app/runs/[id]/architecture/*` | Solution Architect and its page | 9 |
| `templates/<sector>/kit/*`, `templates/<sector>/app/*` | 4 sector kits and Next.js starters | 10 |
| `services/api/poc_studio/agents/screens.py`, `schemas/screenpack.py`, `screens/validate.py` | Prototype Builder: ScreenPack and anchor validation | 11 |
| `services/api/poc_studio/sandbox/` (`runner.py`, `errors.py`), `agents/port.py` | folder or Docker runner, build loop, error-line extraction, Next.js port | 12 |
| `services/api/poc_studio/preview/manager.py`, `routes/preview.py`, `routes/artifacts.py` (download plus file tree); `apps/web/app/runs/[id]/prototype/*` | preview servers, proxy, artifact downloads, Prototype page | 13 |
| `eval/run_eval.py` (`--stage build`) | build-stage KPI after increment 4 | 13b |
| `services/api/poc_studio/media/deck_runtime/` (vendored), `media/assemble.py`, `tests/deck/*` | deck engine and deterministic assembler | 14 |
| `services/api/poc_studio/agents/pitch.py`, `schemas/deck.py`, `media/pptx.py`, `media/docs.py` | dk-data slide plan, Haiku polish, docs, pptx | 15 |
| `services/api/poc_studio/media/video.py`; `apps/web/app/runs/[id]/deck/*` | MP4 recorder; Deck and video page | 16 |
| `services/api/poc_studio/qa/` (`checks.py`, `secrets.py`, `routing.py`), `agents/qa.py` | QA Reviewer, secret and PII scan, send-back routing | 17 |
| `services/api/poc_studio/github/` (`client.py`, `publish.py`), `agents/repo.py`; `apps/web/app/runs/[id]/publish/*` | Gate 2, repo publish (mock or live), Delivered | 18 |
| `services/api/poc_studio/routes/revise.py` (revise, retry, budget); `apps/web/components/run/budget-banner.tsx` | Request changes, retry with a note, budget raise | 19 |
| `apps/web/components/run/request-changes.tsx` | modal shell (Task 8); wired to the API in Task 19 | 8, 19 |
| `services/api/poc_studio/graph/build.py` (final wiring), `tests/integration/test_full_run.py`, `apps/web/e2e/journey.spec.ts` | full graph wiring, both-gates integration, E2E journey | 18b |
| `services/api/poc_studio/share/export.py`, `routes/share.py` (including `POST /share-export`), `routes/templates.py`, `retention.py`; `apps/web/app/share/[token]/*` (own root layout), `app/settings/*`, `app/templates/*` | share zip, public share page, Settings, Templates | 20 |
| `eval/run_eval.py` (full stages), `docs/eval/README.md` | full KPI run over the 10 fixtures (opt-in live) | 21 |
| `scripts/owner/check-github-token.sh` | owner token check (already written 2026-11-22) | owner |

## Tasks

### Increment 1: skeleton (visible: the Runs page on real tokens)

### Task 1: API skeleton with database and mocks  [independent]
- Goal: `uv run` starts FastAPI on :8000 with `/api/health`, SQLite tables migrated, and the mock switches enforced.
- Files (owned): `package.json`, `scripts/dev.mjs`, `services/api/pyproject.toml`, `uv.lock`, `services/api/poc_studio/{main,config}.py`, `db/*`, `alembic/*`, `routes/schemas.py`, `schemas/screenpack.py`, `schemas/deck.py`, `docs/decisions.md`, `.env.example` (new variable names: `LLM_PROVIDER`, `GITHUB_MODE`, `APP_ENV`, `RUN_BUDGET_USD`, `MONTHLY_CAP_USD`, `EVAL_LIVE`, `RETENTION_DAYS`).
- Interface: `GET /api/health` returns `{status:"ok", llm_provider, github_mode, db:"ok"}`; `GET /api/runs` returns `RunSummary[]`.
- Test first: `services/api/tests/test_health.py`:
  - health returns ok and reports `llm_provider=mock` under test;
  - `Settings(APP_ENV="production", LLM_PROVIDER="mock")` raises.
- Steps:
  1. `uv init` in `services/api` and add the full dependency set at its current latest versions (`uv.lock` pins them and is committed):
     - app and data: fastapi, uvicorn, pydantic-settings, sqlalchemy, alembic, sse-starlette, httpx, openai, tiktoken;
     - orchestration: langgraph, langgraph-checkpoint-sqlite, aiosqlite;
     - inputs and media: pypdf, python-docx, lxml, cssselect, playwright, imageio-ffmpeg, python-pptx;
     - dev: pytest, pytest-asyncio, ruff, pyright.
  2. Create the tables from spec sections 7 and 7b as SQLAlchemy models (including `runs.preview_pid` and `runs.preview_port`) and an Alembic initial migration. The database is at `data/poc-studio.sqlite`.
  2b. Write `schemas/screenpack.py` and `schemas/deck.py` exactly as in spec 7a and 7b (ScreenPack, Screen, Anchor, DeckPlan, Slide, Step, Figure), and every endpoint request and response model in `routes/schemas.py`.
  2c. Write `docs/decisions.md` with the resolved values from Global constraints.
  3. Write the health and empty runs routes, and the `schemas.py` models for them.
  4. Root `package.json` with workspaces `apps/*`. `scripts/dev.mjs` runs `uv run uvicorn …` and `npm --workspace apps/web run dev` together and stops both on Ctrl+C.
- Verify: `cd services/api && uv run pytest -q` passes, and `uv run alembic upgrade head` exits 0.
- Commit: `API skeleton: FastAPI, SQLite schema, mock switches`

### Task 2: Web shell and Runs page  [after: 1]
- Goal: Next.js 16 app on :3000 that looks like the approved preview: rail, phone tab bar, and the Runs list with loading, empty and error states read from the API.
- Files (owned): `apps/web/**`.
- Interface: `lib/api.ts` exports `api.runs.list()`. Types come from `npm run gen:types`, which runs `openapi-typescript http://127.0.0.1:8000/openapi.json -o lib/api-types.ts`.
- Test first: `apps/web/__tests__/runs-states.test.tsx` (Vitest + Testing Library) checks that the empty state shows "Start your first run" and the error state names port 8000.
- Steps:
  1. `npx create-next-app@latest apps/web --ts --tailwind --app --no-src-dir`. Add `lucide-react` and `sileo`, and add shadcn/ui as needed.
  2. Port `tokens.css` and the Geist fonts (`@fontsource-variable/geist`, `geist-mono`). Rebuild the shell components from `design/preview/src/screens/01-runs.html` and `styles.css`, without pasting the markup.
  3. Mount the sileo `Toaster` once (bottom-right), with the title-case and z-index overrides from the sileo skill.
- Verify:
  - `npm --workspace apps/web run build` succeeds;
  - `npm --workspace apps/web test` passes (covers the empty, error and loading states with a mocked fetch);
  - with `npm run dev` running, `npx playwright test e2e/runs-empty.spec.ts` sees "Start your first run".
- Commit: `Web shell and Runs page on approved tokens`

### Task 3: CI and root scripts  [after: 2]
- Goal: one command runs every check locally and in GitHub Actions.
- Files (owned): `.github/workflows/ci.yml`, root `package.json` scripts (`test`, `lint`, `typecheck`).
- Test first: none (configuration). The check is the workflow run itself.
- Steps:
  1. Add root scripts:
     - `lint`: ruff, then `eslint .` with `eslint-config-next`. Check the Next.js 16 docs first; `next lint` was removed.
     - `typecheck`: pyright through uv, then `tsc --noEmit`.
     - `test`: pytest with `-m "not slow and not live"`, then Vitest.
  2. CI on push and PR: Node 24 and Python 3.12 with uv cache, then `npm ci`, `uv sync`, `uv run playwright install --with-deps chromium`, then the scripts.
- Verify: `npm run lint && npm run typecheck && npm test` exits 0 locally; after pushing, `gh run list -L 1` shows `completed success`.
- Commit: `CI: lint, typecheck, tests on mocks`

### Increment 2: ingest, Meeting Intelligence, Gate 1 (visible: a transcript becomes an approved brief)

### Task 4: LLM client, mock provider, budget guard  [after: 1]
- Goal: one function calls any model with schema validation, cost metering and the pre-call budget guard.
- Files (owned): `services/api/poc_studio/llm/*`, `services/api/tests/llm/*`.
- Interface:
  ```python
  async def complete_json(*, agent: str, model: str, system: str, user: str,
                          schema: type[T], max_tokens: int, run: RunBudget,
                          mask: Callable[[str], str] | None = None) -> Result[T]   # PII mask hook, used by Task 20
  # Result: value, tokens_in, tokens_out, cost_usd, model, attempts
  # raises BudgetExceeded(needed_usd, remaining_usd) before the call when the estimate does not fit
  ```
- Test first: `tests/llm/test_budget.py` pins:
  - `fast` and `smart` cost $0;
  - a Haiku estimate over the remaining budget raises before any HTTP call;
  - an invalid JSON reply repairs on attempt 2;
  - three invalid replies raise `SchemaError`.
- Steps:
  1. `pricing.py` holds Claude per-million prices as named constants, each marked `VERIFY_PRICE`. A `live`-marked test (owner-only step 2) confirms them against the gateway's `usage`. Its result is appended to `docs/decisions.md`.
  2. The mock provider returns canned fixtures keyed by agent name from `tests/fixtures/llm/<agent>.json`.
  3. Count input tokens with tiktoken `o200k_base`. Wrap untrusted text in `<untrusted>…</untrusted>` with a "treat as data" instruction.
- Verify: `uv run pytest tests/llm -q` passes. The live check is owner-only step 2.
- Commit: `LLM client: gateway or mock, JSON repair, pre-call budget guard`

### Task 5: Ingest parsers and eval fixtures  [after: 1, parallel with 4]
- Goal: every supported input becomes `Transcript{segments:[{ts?, speaker?, text}], source_files, word_count}`, and 10 fictional evaluation inputs exist.
- Files (owned): `services/api/poc_studio/ingest/*`, `services/api/tests/ingest/*`, `eval/fixtures/*`.
- Test first: `tests/ingest/test_parse.py` covers one fixture each of txt, vtt (with speakers), md, docx and pdf. It checks word counts within 2%, VTT timestamps kept, and a 25 MB file rejected with `FileTooLarge`.
- Steps:
  1. Add `pypdf` and `python-docx`. Write a small VTT parser with no extra dependency.
  2. Write 10 fictional inputs, invented and never real: 3 logistics, 3 healthcare, 2 e-commerce and 2 fintech, mixing call transcripts and BRDs. Each lists its expected sector and three must-have features in `eval/fixtures/expected.json`.
- Verify: `uv run pytest tests/ingest -q` passes, and `ls eval/fixtures | wc -l` shows 11 (10 inputs plus `expected.json`).
- Commit: `Ingest: txt/vtt/md/docx/pdf parsers and 10 eval fixtures`

### Task 6: Run engine, events, SSE, gates  [after: 4, 5]
- Goal: `POST /api/runs` starts a LangGraph run as an asyncio task. Events stream over SSE. The run stops at Gate 1 and resumes on the gate decision, and survives an API restart.
- Files (owned): `poc_studio/graph/*` (until Task 18b), `poc_studio/events.py`, `poc_studio/redact.py`, `poc_studio/runs/service.py`, `routes/runs.py`, `routes/events.py`, `routes/gates.py`, `tests/graph/*`.
- Interface:
  - the graph order from spec 7b, with the agent nodes as stubs that later tasks replace;
  - `POST /api/runs/{id}/gates/{scope|publish}` with body `{decision:"approve"|"changes", edits?:object, note?:str}`;
  - SSE events in the spec 7b shape, with `Last-Event-ID` replay from the `events` table.
- Test first: `tests/graph/test_lifecycle.py`, with the mock LLM and a real SQLite temp file, checks that:
  - a run reaches `waiting_gate1`;
  - approving resumes it to the next stub;
  - after recreating the app (a simulated restart), the run resumes from its checkpoint;
  - SSE replay from id 3 returns events 4 and up.
- Steps:
  1. Define `RunState` as a TypedDict with the spec 7 fields, plus `screenpack` and `budget`.
  2. Gates use `interrupt()` and resume with `Command(resume=…)`.
  3. The event bus is in-process, using asyncio queues per subscriber. Every event is also written to `events`.
  4. `redact.py` masks known key patterns (spec 8) in every event and log line before it is written. Test: an event containing a `ghp_` token is stored redacted.
  5. `graph/registry.py` defines `NodeSpec`. Nodes that do not exist yet are stubs that pass the state through. Gate 1 "changes" with a note re-runs intelligence (tested here).
  6. Map `BudgetExceeded` from any node to `paused_budget`, with a checkpoint before the call.
- Verify: `uv run pytest tests/graph -q` passes.
- Commit: `Run engine: LangGraph with gates, SQLite checkpoints, SSE events`

### Task 7: Meeting Intelligence agent  [after: 6]
- Goal: a transcript becomes a validated `requirements.json`: ranked features with confidence and source timestamps, constraints with a `confirmed` flag, stakeholders, and action items with owners.
- Files (owned): `agents/intelligence.py`, `schemas/requirements.py`, `tests/agents/test_intelligence.py`, `tests/fixtures/llm/intelligence.json`.
- Test first: on the mock, the fixture output validates. The node writes the artifact `requirements` v1 and the step row with model `fast` and cost 0. A constraint not found in the text is marked `confirmed=false`.
- Steps:
  1. Write the prompt with the schema embedded, using the `fast` model.
  2. Post-validation: drop features with no source text and log a warning event.
- Verify: `uv run pytest tests/agents/test_intelligence.py -q` passes. A live run on one fixture is owner-only step 2.
- Commit: `Meeting Intelligence agent with requirements schema`

### Task 8: New run, sub-nav, timeline, Gate 1 pages  [after: 2, 6, 7]
- Goal: the owner uploads files, watches the timeline live, then edits and approves the brief, as in the preview's New run, Live run and Gate 1 screens.
- Files (owned): `apps/web/app/runs/new/*`, `apps/web/app/runs/[id]/layout.tsx`, `app/runs/[id]/page.tsx`, `app/runs/[id]/brief/*`, `apps/web/components/run/*` (`request-changes.tsx` here is the modal shell only, wired in Task 19).
- Test first: `apps/web/e2e/gate1.spec.ts` (Playwright, API on mocks):
  - upload a fixture, see the timeline steps appear, open Brief;
  - edit the budget field and click "Approve brief" in the sticky bar;
  - see the toast "Brief approved";
  - at 375 px wide, the bar is visible without scrolling.
- Steps:
  1. The sub-nav in `layout.tsx` shows the run id, client, sector, a live status badge and tabs, and is sticky.
  2. The timeline reads SSE through `EventSource`. Each step shows model, tokens and `$cost / model`, and its log is collapsed in `<details>`.
  3. The sector picker is a custom combobox with an inline "Create".
  4. Add an E2E case: "Re-extract with a note" returns the run to intelligence, and a new brief version appears.
  5. Add a phone-width (375 px) case for the Timeline: the sub-nav tabs scroll and the step logs stay collapsed.
- Verify: `npm --workspace apps/web run e2e -- gate1` passes, and `npm --workspace apps/web run build` succeeds.
- Commit: `New run, run sub-nav, live timeline, Gate 1 brief`

### Increment 3: Solution Architect (visible: an architecture page with a diagram and costs)

### Task 9: Solution Architect agent and page  [after: 8]
- Goal: `architecture.md` with Mermaid, model picks and a monthly cost table, rendered at `/runs/[id]/architecture`. On phone, the tables fall back to cards.
- Files (owned): `agents/architect.py`, `schemas/architecture.py`, `tests/agents/test_architect.py`, `tests/fixtures/llm/architect.json`, `apps/web/app/runs/[id]/architecture/*`, `apps/web/components/architecture/*`.
- Test first: the mock output validates. The cost total equals the sum of its lines. The Mermaid text passes `mermaid.parse` in a Vitest test.
- Steps: `smart` model; render with `mermaid` client-side; tables in `overflow-x:auto` wrappers, with the `data-label` card fallback below 680 px.
- Verify: `uv run pytest tests/agents/test_architect.py -q` passes, and `npm --workspace apps/web test -- architecture` passes.
- Commit: `Solution Architect agent and architecture page`

### Increment 4: Prototype Builder (visible: a screen pack, a building Next.js app, and a live preview)

### Task 10: Sector kits and starters  [after: 1, parallel with 4-9]
- Goal: four sectors (logistics, healthcare, e-commerce, fintech), each with `kit/` (product tokens, 3 example screens as fragments, `selectors.md`) and `app/` (a Next.js 16 starter that builds).
- Files (owned): `templates/**`.
- Test first: `services/api/tests/templates/test_kits.py` checks that each kit's example screens use only classes defined in its CSS, and that every fragment has at least 3 `data-anchor` elements.
- Steps:
  1. Logistics first. The other three follow the same structure.
  2. Product CSS is scoped under `.pf .<app_class>`.
  3. Each starter carries a layout, a nav and the tokens.
- Verify:
  - `uv run pytest tests/templates -q` passes;
  - `for s in logistics healthcare ecommerce fintech; do (cd templates/$s/app && npm ci && npm run build) || exit 1; done` exits 0 (marked `slow`; runs locally).
- Commit: `Four sector kits with Next.js starters`

### Task 11: Prototype Builder: ScreenPack  [after: 9, 10]
- Goal: the brief, architecture and kit become a validated `ScreenPack` of 6 to 12 screens, and every anchor selector matches its HTML.
- Files (owned): `agents/screens.py`, `screens/validate.py`, `tests/agents/test_screens.py`, `tests/fixtures/llm/screens.json`. It imports `schemas/screenpack.py` from Task 1.
- Interface: `validate(pack) -> list[Issue]`. The schemas come from Task 1.
- Test first:
  - a fixture pack passes;
  - an anchor that matches nothing fails with a named issue;
  - `step_css` outside `.pf.sl-<id>[data-step]` is rejected;
  - product CSS not scoped under `.pf .<app_class>` is rejected.
- Steps:
  1. Add `lxml` and `cssselect` for selector checks.
  2. Use the `smart` model. Invalid packs go back to the model with the issue list, at most 2 repairs.
- Verify: `uv run pytest tests/agents/test_screens.py -q` passes.
- Commit: `Prototype Builder: ScreenPack with anchor validation`

### Task 12: Sandbox, Next.js port and build loop  [after: 11]
- Goal: the ScreenPack becomes Next.js pages in a copy of the starter. `npm run build` runs in the sandbox with up to 3 fix attempts. Errors are captured as file, line, column, message and excerpt.
- Files (owned): `sandbox/runner.py`, `sandbox/errors.py`, `agents/port.py`, `tests/sandbox/*`, `tests/fixtures/llm/port.json` (a canned port output that really builds against the logistics starter).
- Interface: `async def build(run_dir, attempt) -> BuildResult{ok, duration_s, error?:{file,line,col,message,excerpt}}`.
- Test first:
  - `test_errors.py` parses 4 captured Next.js and TypeScript error outputs into the right file, line, column and message;
  - `test_env.py` checks that the child environment contains no `OPENAI_API_KEY` or `GITHUB_TOKEN`;
  - a `slow` test builds the logistics starter in folder mode.
- Steps:
  1. Use Docker when `docker info` succeeds, otherwise folder mode.
  2. Run `npm ci --prefer-offline` with a shared cache. Timeouts: install 180 s, build 90 s.
  3. The port prompt keeps class names and CSS verbatim.
- Verify: `uv run pytest tests/sandbox -q` passes, and `uv run pytest -m slow tests/sandbox -q` passes locally.
- Commit: `Sandbox runner, Next.js port and build-fix loop`

### Task 13: Preview servers and Prototype page  [after: 8, 12]
- Goal: a built app is served on ports 4300 to 4399 behind `/api/runs/{id}/preview/`. The Prototype page shows it with a desktop and phone toggle, "Open in new tab", a file tree, the build log and "Request changes".
- Files (owned): `preview/manager.py`, `routes/preview.py`, `tests/preview/*`, `apps/web/app/runs/[id]/prototype/*`.
- Test first:
  - the manager allocates a free port, reuses it per run and stops it after the idle timeout (a fake clock);
  - on API start, orphan pids recorded in `runs` are killed (`taskkill /T /F` on Windows).
- Also: `routes/artifacts.py` adds `GET /api/runs/{id}/artifacts/{type}` (download) and `GET /api/runs/{id}/files` (file tree), with tests.
- Verify: `uv run pytest tests/preview tests/routes/test_artifacts.py -q` passes. Then, marked `slow`, a manager test builds the Task 10 logistics starter, serves it, and gets HTTP 200 with `<html` through the proxy.
- Commit: `Preview servers, proxy, artifact downloads, Prototype page`

### Task 13b: Build-stage KPI  [after: 13]
- Goal: measure "8 of 10 build" (spec success measure for 2026-12-06) before the deck work starts.
- Files (owned): `eval/run_eval.py` (the `--stage build` path only).
- Test first: `--stage build --dry` on the mock provider prints 10 rows.
- Verify: `uv run python eval/run_eval.py --stage build --dry` prints a 10-row table. The live run is owner-only step 3.
- Commit: `Build-stage eval over 10 fixtures`

### Increment 5: deck and video (visible: the reference-format deck and an MP4 in the app)

### Task 14: Vendored deck engine and assembler  [after: 1, parallel with 4-13; runs on the owner's machine, where `reference/` exists]
- Goal: `assemble(screenpack, dk_data, logo) -> html` writes one self-contained file in the exact reference format.
- Files (owned): `media/deck_runtime/` (`runtime.js`, `chrome.css`, `README.md` with provenance), `media/assemble.py`, `tests/deck/*` (marked `browser`), `tests/fixtures/deck/*` (a fictional ScreenPack and DeckPlan built with the Task 1 schemas).
- Interface: `assemble(pack: ScreenPack, plan: DeckPlan, logo_data_uri: str | None) -> str`.
- Test first: `tests/deck/test_contract.py` (pytest + Playwright Chromium) on the fixture deck checks that:
  - no `src` or `href` starts with `http`;
  - `window.__deck.ready === true`;
  - every step's spotlight resolves, with no "Spotlight target not found" in the console;
  - `#2.1` deep-links to slide 2, step 1;
  - the stage is 1280x720.
- Steps:
  1. From `reference/hse-deck/…html`, copy **only**:
     - the chrome CSS block (from the top of `<style>` to the `.pf{` product rules);
     - the runtime `<script>` (the one that reads `#dk-data`).

     Copy no product CSS, templates, `__dkScripts` or logo. The README records the source file, the date and amendment 9.
  2. The assembler emits:
     - `<style>` with the chrome CSS plus the pack's `product_css` plus every screen's `step_css`;
     - one `<template id="tpl-…">` per screen;
     - `#dk-data`;
     - `__dkScripts`;
     - the runtime.
  3. Chromium comes from owner-only step 1.
- Verify: `uv run pytest tests/deck -q` passes, and `! grep -rqE "HSE|Method Statement" services/api/poc_studio/media/deck_runtime/` exits 0.
- Commit: `Deck engine (vendored chrome and runtime) and assembler`

### Task 15: Pitch and Docs agent  [after: 11, 14]
- Goal: a `DeckPlan` (the dk-data) built from the ScreenPack and the brief, plus the executive summary, user flows and `.pptx`. Haiku polishes only titles and captions, under the budget guard.
- Files (owned): `agents/pitch.py`, `media/pptx.py`, `media/docs.py`, `tests/agents/test_pitch.py`, `tests/fixtures/llm/pitch.json`. It imports `schemas/deck.py` from Task 1.
- Test first:
  - spotlights use only `anchors[].selector` from the pack;
  - close figures each carry a source found in the requirements or architecture;
  - 9 to 12 slides with the welcome, overview, area, play and close kinds;
  - on a $0.001 remaining budget the polish step raises `BudgetExceeded` and the run goes to `paused_budget`;
  - the `.pptx` opens with python-pptx and has the same slide count.
- Verify: `uv run pytest tests/agents/test_pitch.py -q` passes.
- Commit: `Pitch and Docs: slide plan, Haiku polish, docs, pptx`

### Task 16: MP4 recorder and Deck and video page  [after: 8, 14, 15]
- Goal: after Gate 2, the approved deck is recorded to `<slug>-walkthrough.mp4` (2 to 3 minutes, chapters from slide titles). The Deck page shows the deck in a 16:9 iframe with "Open full screen" and an MP4 player with chapters and "Download MP4", as in approved sample v3.
- Files (owned): `media/video.py`, `tests/media/test_video.py`, `apps/web/app/runs/[id]/deck/*`, `apps/web/components/deck/*`.
- Test first (marked `browser`): on the fixture deck, `record(deck, hold_s=0.3)` produces:
  - an MP4 with H.264, checked through the `imageio-ffmpeg` probe;
  - a duration over 5 s;
  - a chapters JSON that matches the slide titles;
  - the hands-on slide skipped.

  After recording, `video_check()` appends "MP4 plays (duration > 0)" to `qa_report`. This is the spec 7a MP4 check, moved here because the video is made after QA.
- Steps:
  1. Add `imageio-ffmpeg`. Playwright records WebM at 1280x720, then the bundled ffmpeg converts it to MP4 with `-c:v libx264 -pix_fmt yuv420p -movflags +faststart`.
  2. Hold time per step is 3 s plus 25 ms per caption character, scaled to fit 120 to 180 s.
  3. The player shows a "video missing" state when the file is absent.
- Verify: `uv run pytest tests/media -q` passes, and `npm --workspace apps/web run e2e -- deck` passes (the iframe loads, the video's `readyState` is at least 1).
- Commit: `Walkthrough MP4 recorder and Deck and video page`

### Increment 6: QA, Gate 2, publish (visible: a real or mocked repo with issues)

### Task 17: QA Reviewer and secret scan  [after: 12, 15]
- Goal: all checks from spec 7a and 7b run, except the MP4 check (Task 16). Failures are routed by the 7b table (at most 2 send-backs per run), and `qa_report` is written. The share-zip scan exempts the stakeholder names from `requirements.json`.
- Files (owned): `qa/checks.py`, `qa/secrets.py`, `qa/routing.py`, `agents/qa.py`, `tests/qa/*`.
- Test first:
  - each check has a pass and a fail fixture;
  - the secret scanner flags `ghp_…`, `sk-…`, a private key block and a `.env` value matched by hash;
  - the routing test sends "spotlight unresolved" to pitch and stops after 2 send-backs;
  - "Next.js build failed" is report-only.
- Verify: `uv run pytest tests/qa -q` passes.
- Commit: `QA Reviewer with routing and secret/PII scan`

### Task 18: Gate 2, repo publish, Delivered  [after: 13, 16, 17]
- Goal: Gate 2 shows the QA report and repo options in the sticky bar. Publishing creates a private repo with the README, `.env.example`, a CI workflow and the first push, then opens issues from action items. Delivered links everything.
- Files (owned): `github/client.py`, `github/publish.py`, `agents/repo.py`, `tests/github/*`, `apps/web/app/runs/[id]/publish/*`.
- Test first:
  - in `GITHUB_MODE=mock`, publish records the planned API calls (create repo private, push, N issues) and no network call happens;
  - a secret-scan hit blocks the push;
  - the token goes through `http.extraheader` and never appears in `git remote -v`.
- Steps:
  1. REST calls go through `httpx`: `POST /user/repos` then `POST /repos/{o}/{r}/issues`.
  2. Push with the git CLI.
  3. Live mode needs `GITHUB_MODE=live` and the Gate 2 click.
- Verify: `uv run pytest tests/github -q` passes, and `npm --workspace apps/web run e2e -- publish` passes (mock).
- Commit: `Gate 2, GitHub publish (mock/live), Delivered page`

### Task 18b: Final graph wiring, both-gates integration, E2E journey  [after: 18]
- Goal: the real graph from spec 7b replaces the stubs:
  - the pitch and port fan-out, then assemble, then QA with send-back (at most 2);
  - Gate 2, then video, then repo;
  - a failed port does not block Gate 2.
- Files (owned): `graph/build.py`, `tests/integration/test_full_run.py`, `apps/web/e2e/journey.spec.ts`.
- Test first:
  - `test_full_run.py` (mock LLM, real SQLite, folder sandbox, marked `slow` for the build) runs a fixture through both gates to `delivered`. It asserts the step order and the artifacts (requirements, architecture, screenpack, deck, video, qa_report), and that paid spend is at most the budget.
  - A second case uses a failing port fixture: the run still reaches `waiting_gate2` with "repo code did not build".
- Verify:
  - `uv run pytest tests/integration -q` passes;
  - `npx playwright test e2e/journey.spec.ts` (New run, Gate 1, mocked build, Gate 2, Delivered, plus a 375 px pass on the Gate 2 bar) passes.
- Commit: `Wire the full graph; both-gates integration and E2E journey`

### Increment 7: hardening (visible: request changes, budget pause, share zip)

### Task 19: Request changes, retry with a note, budget raise  [after: 18b]
- Goal: a note on any artifact reruns only its owning agent. A failed build can be retried with a note or 3 more attempts. A `paused_budget` run resumes after a raise or the "use the free model" choice.
- Files (owned): `routes/revise.py` (`POST …/artifacts/{type}/revise`, `POST …/retry`, `POST …/budget`), `tests/routes/test_revise.py`, `apps/web/components/run/budget-banner.tsx`. It also wires `request-changes.tsx`, whose shell Task 8 made.
- Test first:
  - revising the prototype reruns screens and port but not intelligence (asserted through the step rows);
  - a budget raise resumes from the checkpoint with no duplicate paid call.
- Verify: `uv run pytest tests/routes/test_revise.py -q` passes.
- Commit: `Request changes, retry with note, budget pause and raise`

### Task 20: Share zip, public share page, Settings, Templates, PII mask, retention  [after: 18b; parallel with 19]
- Goal:
  - the share zip contains `index.html` (summary, MP4 player, deck link), `deck.html`, the walkthrough MP4 and `summary.pdf`;
  - `/share/[token]` uses its own root layout with no app chrome;
  - the Settings page shows key names only, gateway test and budget;
  - the Templates page lists the kits and their build rates;
  - the optional PII mask runs before LLM calls.
- Files (owned): `share/export.py`, `routes/share.py`, `routes/settings.py`, `routes/templates.py`, `retention.py`, `tests/share/*`, `apps/web/app/share/[token]/*`, `apps/web/app/settings/*`, `apps/web/app/templates/*`, `poc_studio/pii.py`.
- Test first:
  - the zip passes the secret and PII scan and has no `http` asset links;
  - the share page HTML contains no link to `/settings`, `/runs` or `/templates`;
  - the PII mask replaces emails and phone numbers and keeps stakeholder names in the deck;
  - `summary.pdf` is made with Playwright `page.pdf` (marked `browser`);
  - with `RETENTION_DAYS=1`, the inputs of runs older than 1 day are deleted on API start, and the artifacts are kept.
- Verify: `uv run pytest tests/share -q` passes, and `npm --workspace apps/web run e2e -- share` passes.
- Commit: `Share zip and public page, Settings, Templates, PII mask`

### Task 21: KPI evaluation  [after: 19, 20]
- Goal: `EVAL_LIVE=1 uv run python eval/run_eval.py --stage full` runs the 10 fixtures end to end (the gates auto-approved in eval mode only, and publish mocked). It writes `eval/report.md` with builds-first-time, median agent time, paid spend per run and secret findings.
- Files (owned): `eval/run_eval.py`, `docs/eval/README.md`.
- Test first: `--dry` on the mock provider produces a report with 10 rows.
- Verify: `uv run python eval/run_eval.py --stage full --dry` prints a 10-row table. The live run is owner-only step 3.
- Commit: `KPI evaluation over 10 fixtures`

## Owner-only steps

Run these from the project folder. None of them prints a secret. Each one waits for your yes at the point shown.

1. **Chromium for Playwright** (before Task 14): `! uv --directory services/api run playwright install chromium` (about 150 MB, free).
2. **Live model checks** (Tasks 4 and 7): `! EVAL_LIVE=1 uv --directory services/api run pytest -m live -q`. This confirms the Claude prices and runs one fixture brief. Expected spend is under $0.02.
3. **Live KPI runs** (Tasks 13b and 21): `! EVAL_LIVE=1 uv --directory services/api run python ../../eval/run_eval.py --stage build`, then `--stage full`. Expected spend is under $0.50 in total. It needs npm network access.
4. **GitHub token** (before Task 18 live): **the token in `.env` is rejected today (HTTP 401, checked 2026-11-22).**
   1. Make a fine-grained token at github.com/settings/personal-access-tokens:
      - Repository access: All repositories;
      - Administration, Contents and Issues: Read and write.
   2. Paste it into `.env` as `GITHUB_TOKEN` yourself.
   3. Run `! bash scripts/owner/check-github-token.sh`.
5. **First live publish** (Task 18): set `GITHUB_MODE=live` in `.env` yourself, then click Publish on one run. This creates a real private repo on `Jegathpranava`.
6. **Optional:** install Docker Desktop to switch the sandbox to container mode.

## Parked (NEXT_STEPS.md)

- Vercel preview links for the share page and the prototype (on your yes for each deploy).
- Audio transcription (local Whisper).
- Langfuse traces; Postgres switch; more sector kits; Jira and Trello export.
