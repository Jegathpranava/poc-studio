# PoC Studio: design spec

Date: 2026-11-22. Status: draft for the owner's plan approval.
Inputs: `docs/requirements/original-brief.md` (verbatim brief), `technical-solution-proposal.txt` (PDF), `problem-statement.txt` (DOCX), `owner-direction-2026-11-22.md`, `docs/intake/answers.json`, and the approved UI sample `design/preview/preview.html` (`docs/intake/approval.json`). Where this spec differs from those, this spec wins.

## 1. Intent and why

Pre-sales PoCs take 3 to 5 business days and over 60% of billable hours: summarising meetings, drafting architecture, scaffolding demo sites, making decks. PoC Studio is a local, single-user tool for the owner. One transcript or requirements doc (BRD, TRD, notes) goes in. Within about 5 minutes of agent time, it produces:

- a brief with action items;
- an AI architecture spec with costs;
- a building sector prototype;
- a deck, a walkthrough video and docs;
- a GitHub repo on the owner's account.

The owner approves at two gates. It is built on a budget: everything runs locally or on free gateway models, and only the deck polish is a paid call.

## 2. Goals, non-goals, anti-goals

**Goals**
- G1. Transcript or doc in, all deliverables out, in under 5 minutes of agent time (median).
- G2. 8 of 10 test inputs produce a prototype that passes `npm run build`.
- G3. Paid model spend under $0.05 per run, shown live, with a hard pause at the limit.
- G4. Nothing leaves the machine before Gate 2. Every step is visible, logged and resumable.

**Non-goals (v1)**
- Login, teams, multi-tenant.
- Redis or Celery, S3, pgvector, E2B, Langfuse.
- Audio transcription.
- Jira or Trello export.
- Auto-deploying client prototypes.

**Anti-goals** (a failure even if it works)
- A generated repo or share export contains a secret or the owner's personal data.
- A run silently spends past its budget, or pushes to GitHub without the Gate 2 click.
- Monolith files: agents, routes and UI components must stay in separate modules.
- Generated prototypes that look like template slop: each must carry the client's name, sector and features from the brief.

## 3. Amendments to the brief (this spec wins)

1. (2026-11-22) Next.js 16 instead of 14. Same App Router; 14 is out of support.
2. (2026-11-22) The input accepts transcripts and requirements docs: `.txt`, `.vtt`, `.md`, `.docx` and `.pdf`, several files per run.
3. (2026-11-22) The Pitch and Docs agent also produces a 30 to 60 second walkthrough video of the built prototype.
4. (2026-11-22) Budget build: SQLite plus local files instead of Postgres plus S3; asyncio tasks instead of Redis/Celery; local Docker or a plain folder instead of E2B; a fine-grained personal token instead of a GitHub App; per-step cost logging instead of Langfuse.
5. (2026-11-22) Single user on 127.0.0.1, with no auth.
6. (2026-11-22) The repo lives on the personal account `Jegathpranava`, which is public. Generated client repos default to private.
7. (2026-11-22) UI changes from the sample review, all approved:
   - a sticky run sub-nav (run ID, sector, live status);
   - collapsible per-step logs;
   - model, tokens and cost on every step;
   - failing line highlighted, with "Attempt X of 3";
   - sticky gate action bars;
   - card fallback for tables on phone;
   - an isolated public share layout;
   - "Open in new tab" on the prototype.

8. (2026-11-22, owner request) **Deck and prototype output format.**
   - The client-facing prototype and deck is one self-contained HTML deck in the exact format of `reference/hse-deck/hse-risk-assesment-site-safety-advisor.html`:
     - a 1280x720 stage that scales;
     - template-based product frames;
     - step spotlights with caption bubbles;
     - welcome, overview, area, play and close slides.

     The contract is in section 7a.
   - The deck and share views embed an MP4 player for the run's walkthrough video. The reference MP4 is `reference/hse-deck/skyform_hse_demo_video.mp4`.
   - This replaces the earlier Reveal.js deck. The `.pptx` export stays as a static extra. The Next.js app remains the code that goes into the GitHub repo.
   - The `reference/` folder is git-ignored because this repo is public.

9. (2026-11-22, owner) The deck engine is vendored and committed to this public repo at `services/api/poc_studio/media/deck_runtime/`. It covers only the runtime JS and chrome CSS: no HSE screens, logo, images or video. CI uses it directly.
10. (2026-11-22, owner) The walkthrough MP4 runs about 2 to 3 minutes. Every slide and step is held about 3 s, and the hands-on slide is skipped. This replaces "30 to 60 s" in amendment 3.
11. (2026-11-22, owner) Client sharing in v1 is a share zip that the owner sends: the self-contained deck, the MP4 and a summary page. Nothing is hosted. Vercel preview links are a later increment.

## 4. Stack

| Layer | Choice | Reason |
|---|---|---|
| Web | Next.js 16 App Router, TypeScript, Tailwind v4 (theme mapped from `design/preview/tokens.css`), shadcn/ui, Lucide, sileo | Brief; the same stack as the generated prototypes |
| API | Python 3.12, FastAPI, Pydantic v2, SSE (`sse-starlette`), uv | Proposal |
| Orchestration | LangGraph `StateGraph`, `interrupt()` at the gates, `AsyncSqliteSaver` checkpointer | Proposal; resumable runs with no extra services |
| Data | SQLite through SQLAlchemy 2 and Alembic; artifacts under `runs/<run_id>/` | $0; Postgres later by changing `DATABASE_URL` |
| LLM | Gateway, OpenAI-compatible (`openai` SDK); `fast` for extraction, `smart` for architecture and code, `claude-haiku-5-5` for deck polish only | Brief budget rule |
| Doc parsing | `pypdf`, `python-docx`, a small VTT parser | Input amendment |
| Build sandbox | Docker (`node:22`, npm-only network) when available; otherwise a subprocess in the run folder with no API env vars | Docker is not installed today |
| Deck | Self-contained HTML deck in the reference format: a vendored deck runtime and chrome CSS, assembled deterministically in Python; `python-pptx` for the static export | Amendment 8 |
| Video | Playwright for Python drives the deck's own deep links (`#slide.step`) at 1280x720 and records WebM, then converts to MP4 (H.264) with the `imageio-ffmpeg` bundled binary | Amendments 3 and 8; no system ffmpeg needed |
| GitHub | REST through `httpx` plus the git CLI, with the token passed as an `http.extraheader` (never in the remote URL) | Amendment 4 |
| Tests | pytest, Vitest, Playwright E2E | Section 11 |

## 5. Environment findings (verified 2026-11-22 on the owner's Windows 11 machine)

- `gh` is logged in as `Jegathpranava`, with scopes `repo, workflow, read:org, gist`. The project repo `github.com/Jegathpranava/poc-studio` exists and is pushed.
- Tool versions: Node 24.20.0, Python 3.12.10, uv 0.11.29, git 2.55.
- Docker: not installed. Playwright browsers: not installed. LangGraph: not installed yet; the plan installs it into the project venv.
- `.env` holds these names (values not read into this spec): `OPENAI_BASE_URL`, `OPENAI_API_KEY`, `DEFAULT_FAST_MODEL=fast`, `DEFAULT_SMART_MODEL=smart`, `POLISH_MODEL=claude-haiku-5-5`, `DATABASE_URL` (sqlite), `GITHUB_TOKEN`, `PORT=8000`.
- The gateway `/v1/models` returned 200 with: `fast, smart, vision, embed, guard, claude-sonnet-5-5, claude-opus-5-5, claude-haiku-5-5`.
- Ports 3000, 3100, 8000 and 8100 are free. The plan uses web :3000 and API :8000; prototype previews use 4300 to 4399.

## 6. Architecture

```
 Browser (127.0.0.1:3000)
   Next.js app ── fetch / SSE ──▶ FastAPI (127.0.0.1:8000)
                                   │
                                   ├─ RunService ── LangGraph graph (asyncio task per run)
                                   │     intake → intelligence → [GATE 1 interrupt]
                                   │       → architect → ( builder ∥ pitch ) → video → qa
                                   │       → qa routes failures back (max 2) → [GATE 2 interrupt] → repo
                                   │
                                   ├─ EventBus (in-process) + events table → SSE /runs/{id}/events
                                   ├─ LLM gateway client (mock | gateway), cost meter, budget guard
                                   ├─ Sandbox runner (docker | folder) → npm build, preview server
                                   └─ SQLite (app tables + LangGraph checkpoints), runs/<id>/ files
 Outbound, Gate 2 only: api.github.com, github.com (git push)
 Outbound, any time: gateway.ai.skyformit.com, registry.npmjs.org (sandbox)
```

**Trust boundaries**
- Input files and transcripts are untrusted text.
- Generated code is untrusted. It runs only in the sandbox, without the API's environment variables.
- The API binds to 127.0.0.1 only.
- The share export is the only artifact meant to be handed to the client.

**Module layout** (no monolith files)
- `apps/web/`: `app/` routes, `components/`, `lib/api.ts`.
- `services/api/poc_studio/`:
  - `main.py`, `config.py`
  - `routes/` (runs, gates, artifacts, templates, settings, share)
  - `agents/<agent>.py`: one module per agent, each with its Pydantic I/O
  - `graph/` (state, builder, nodes)
  - `llm/` (client, mock, pricing)
  - `sandbox/`, `github/`, `ingest/`, `media/` (deck, pptx, video), `qa/`, `db/`
- `templates/<sector>/`: four Next.js starters.
- `runs/`: git-ignored.

## 7. Data model and interfaces

**Tables (SQLite)**

| Table | Columns |
|---|---|
| `projects` | id, client_name, sector, created_at |
| `runs` | id (`r_` + 6 hex), project_id, title, status (`queued`, `running`, `waiting_gate1`, `waiting_gate2`, `paused_budget`, `failed`, `delivered`), current_step, paid_usd, tokens_total, budget_usd, started_at, finished_at |
| `agent_steps` | id, run_id, agent, status, attempt, model, tokens_in, tokens_out, cost_usd, started_at, finished_at, error_file, error_line, error_message |
| `artifacts` | id, run_id, type (`requirements`, `architecture`, `prototype`, `deck`, `pptx`, `video`, `docs`, `qa_report`, `share_export`), version, path, sha256, created_at |
| `approvals` | id, run_id, gate (`scope`, `publish`), decision, edits_json, decided_at |
| `events` | id, run_id, ts, agent, level, message; replayed by SSE from `Last-Event-ID` |

**Graph state:** `transcript_refs`, `requirements`, `architecture`, `code_manifest`, `build_result`, `deck`, `video`, `qa_report`, `repo_url`, `budget`.

**Agent contracts** (Pydantic v2; every LLM output is schema-validated and retried up to 2 times on invalid JSON)
- `Requirements`: client, sector, goals, pain_points, features (ranked, with confidence and source timestamp), constraints (each with a `confirmed` flag), budget, timeline, stakeholders, action_items (owner, due).
- `Architecture`: use_case_class, components, mermaid, models (job, model, cost per 1k calls), monthly_cost lines plus total, phases, rationale.
- `CodeManifest`: template id, files written, routes, build attempts, last error (file, line, column, message, code excerpt).
- `DeckPlan`: the dk-data slides from section 7a (9 to 12 slides), plus exec_summary_md and user_flows_md.
- `QAReport`: checks (name, pass, detail, owner_agent), sent_back_count.

**HTTP API**

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/runs` | Multipart files plus client and options. Returns the run id |
| GET | `/api/runs`, `/api/runs/{id}` | Run list and run detail |
| GET | `/api/runs/{id}/events` | SSE stream |
| POST | `/api/runs/{id}/gates/{scope\|publish}` | Approve with edits, or re-extract with a note |
| POST | `/api/runs/{id}/artifacts/{type}/revise` | Note to the owning agent |
| POST | `/api/runs/{id}/retry` | Retry the failed step, optionally with a note and attempts |
| POST | `/api/runs/{id}/budget` | Raise the limit for this run |
| GET | `/api/runs/{id}/artifacts/{type}` | Download an artifact |
| GET | `/api/runs/{id}/preview/` | Reverse proxy to the prototype preview server |
| POST | `/api/runs/{id}/share-export` | Build the share zip |
| GET, PUT | `/api/settings` | Settings |
| GET | `/api/templates` | Template list |
| GET | `/api/health` | Health check |

## 7a. Deck and prototype output contract (amendment 8)

Reference: `reference/hse-deck/hse-risk-assesment-site-safety-advisor.html` (owner's, git-ignored).

**One file, no network.** Inline `<style>` and `<script>`. Images and logos are data URIs; no external fonts or CDNs. The target is under 2 MB without video. The MP4 is a separate file next to it, never base64-embedded.

**Page skeleton** (identical to the reference):
- `#dk-viewport` holds `#dk-stage`, which is 1280x720 and scaled to fit.
- Deck chrome classes: `.dk-head`, `.dk-eyebrow`, `.dk-title`, `.dk-caption`, `.dk-body`, `.dk-frame` (`.with-steps` or `.full`), `.dk-steps` and `.dk-step`, `.dk-bar` with `.dk-progress` and `.dk-count`, `.dk-spot`, `.dk-bubble`, `.dk-cover`, `.dk-figs`, `.dk-play-bar` and `.dk-chip`, `.dk-toast`.
- Theme tokens `--dk-*`, with `--dk-accent` set from `dk-data.accent`.

**Product screens:**
- One `<template id="tpl-<screen-id>">` per screen. Each holds the product UI for that screen, rooted at an app class (for example `<div class="<app> app">`).
- All product CSS is scoped under `.pf` and the app class, so deck chrome and product styles never collide.
- Step states are CSS on `.pf.sl-<screen-id>[data-step="N"] …`. The runtime mounts each template into `.pf-canvas` (1280 px wide) inside `.dk-frame` and sets `data-step`.
- Optional behaviour goes in `window.__dkScripts["<screen-id>"] = function (root, api) {…}`, using `api.onStep`, `api.mode` (`"tour"` or `"play"`) and `api.toast`. Actions in play mode are marked `data-act` and show "Simulated in this demo".
- Icons are CSS-mask Lucide SVGs (`.ic` with `--m`), as in the reference.

**`#dk-data` JSON** (`application/json`):

```json
{
  "title": "…",
  "accent": "#hex",
  "accentInk": "#fff",
  "logo": "<img src='data:…' alt='…'>",
  "dataNote": "Sample data: illustrative",
  "byline": "",
  "productDark": false,
  "playScreens": [{ "id": "…", "label": "…" }],
  "slides": [
    { "id": "welcome", "kind": "welcome", "eyebrow": "…", "title": "…", "caption": "…", "steps": [] },
    { "id": "<screen>", "kind": "overview | area", "eyebrow": "…", "title": "…", "caption": "…",
      "steps": [{ "title": "…", "caption": "…", "spotlight": "<css selector inside the template>" }] },
    { "id": "play", "kind": "play", "title": "Your turn", "caption": "…", "hint": "…", "steps": [] },
    { "id": "close", "kind": "close", "title": "…", "caption": "…",
      "figures": [{ "label": "…", "value": 10, "source": "…", "verified": true }] }
  ]
}
```

**Runtime:**
- The deck runtime and chrome CSS are copied once from the reference into `services/api/poc_studio/media/deck_runtime/` and never generated by an LLM.
- It provides deep links (`#slide.step`), keyboard, touch and fullscreen, count-ups, and the `window.__deck` hook (`ready`, current slide and step). Tests and the video recorder use that hook.

**Who produces what:**
- **Prototype Builder** writes a `ScreenPack` with 6 to 12 screens. Each screen has: id, label, an HTML fragment, scoped CSS, step-state CSS, an optional behaviour script, and the spotlight selectors it exposes. It writes the screens from the approved brief and the sector template's design kit. It also writes the Next.js app for the repo, porting the same screens into pages with the build loop and up to 3 attempts. The ScreenPack is the single source of the screens.
- **Pitch and Docs** writes the `#dk-data` slide plan:
  - the welcome slide;
  - one overview tour;
  - 1 area slide per key screen, with 3 to 5 steps each;
  - a play slide over the main screens;
  - a close slide whose figures come only from the brief or architecture, each marked `verified` with its source.

  Haiku polishes only the titles and captions. It also writes the docs and the `.pptx`.
- **Deck assembler** (deterministic Python, no LLM) merges the runtime, chrome CSS, ScreenPack and `dk-data` into `runs/<id>/deck/<slug>.html`.
- **Video step** opens the assembled deck in Playwright at 1280x720 and steps through every slide and step, holding each for a set time. It records and writes `runs/<id>/deck/<slug>-walkthrough.mp4` with chapters generated from the slides.
- **QA Reviewer**, deck checks:
  - the file is self-contained, with no `http(s)://` in `src` or `href` except links that only show as text;
  - every spotlight selector resolves, and the console has no "Spotlight target not found";
  - `window.__deck.ready` is true;
  - the slide count is in range;
  - the figures appear in the brief or architecture;
  - the MP4 plays (duration above 0).

**Views:**
- The Deck and video page embeds the deck in a 16:9 iframe with "Open full screen", plus an MP4 player with chapters and "Download MP4". The approved sample shows this with the reference files.
- The share view and share export carry the same MP4 player and a link to the self-contained deck.

## 7b. Pipeline, schemas and budgets (resolved after the builder check, Claude's call unless marked)

**Agent order** (replaces "builder ∥ pitch" in section 6):

```
intake → intelligence → GATE 1 → architect → screens (Prototype Builder: ScreenPack)
   → ( pitch: dk-data slide plan  ∥  port: Next.js app + build loop )
   → assemble deck (deterministic) → qa → GATE 2 → video (MP4) → repo
```

- The deck depends only on the ScreenPack, never on the Next.js build.
- A failed Next.js port does not block the deck or Gate 2. QA marks it as failing, and Gate 2 shows "repo code did not build". The owner can publish anyway, retry, or add a note.
- The video is recorded after Gate 2 approval, from the approved deck, so a rejected deck costs no recording time.

**Template, design kit, ScreenPack and pages:**
- `templates/<sector>/` holds two things:
  - `kit/`: the sector's product CSS tokens, 3 example screen fragments and a selector naming guide;
  - `app/`: a Next.js starter with layout, nav and the tokens wired in.
- **Prototype Builder (`smart`)** writes the ScreenPack from the brief, the architecture and `kit/`.
- **Port (`smart`)** turns each ScreenPack screen into `app/<route>/page.tsx`. The class names and the CSS file are kept verbatim, so it is a JSX transform plus data wiring, not a redesign. The build loop runs up to 3 attempts.

**ScreenPack schema** (Pydantic):

```
ScreenPack { app_class: str, accent: hex, product_css: str (scoped under .pf .<app_class>), screens: [Screen] (6..12) }
Screen     { id: slug, label: str, route: str, html: str, step_css: str (only .pf.sl-<id>[data-step] rules),
             script: str | None (window.__dkScripts body), anchors: [Anchor] (3..8), play: bool }
Anchor     { selector: str (must match ≥1 element in html; checked at parse), purpose: str }
```

- Pitch may only use `anchors[].selector` values as spotlights, which is enforced by validation. The selector contract is therefore checked before the deck is assembled.

**QA routing** (a check sends work back to its owner at most 2 times in total per run; after that QA reports and the run goes to Gate 2):

| Check | Goes back to |
|---|---|
| Spotlight unresolved | pitch |
| Deck not self-contained | assembler (a bug; fails the run) |
| Feature or name mismatch | pitch, or screens if a screen lacks the feature |
| Figure without a source | pitch |
| Secret found | port, and the push is blocked |
| Next.js build failed | port (its own 3 attempts already used, so it is only reported) |

**Time budget per step** (target, median): intelligence 30 s; architect 60 s; screens 75 s; pitch and port in parallel 90 s; assemble 2 s; QA 20 s. That is about 4.5 minutes and counts toward G1. Not counted toward G1: time waiting at the gates, video recording (after Gate 2), and repo publish. "Agent time" means the wall clock from the run start to Gate 2 ready, minus the time spent at Gate 1.

Hard limits: npm install 180 s, build 90 s, each LLM call 90 s. JSON repair retries: 2 per call.

**Budget:**
- `budget_usd` defaults to $0.05 per run, and the monthly cap is $5.
- `fast`, `smart`, `vision`, `embed` and `guard` are priced at $0, because the gateway runs them on Ollama.
- Claude models are priced per million tokens in `llm/pricing.py`. Increment 2 checks those prices against the gateway's usage response; the prices are not guessed in this spec.
- **Pre-call guard:** the estimated cost (input tokens counted with tiktoken `o200k_base`, plus `max_tokens` times the output price) must fit the remaining budget. Otherwise the step pauses before the call.
- **Pause:** the run status becomes `paused_budget`. The step is checkpointed before the call. A raise or a "use the free model" choice resumes from that checkpoint, with no partial spend lost.
- Haiku input is capped at 12k tokens: only titles, captions and the brief summary go to it.

**Events (SSE):**
- The event name is `step` or `run`.
- `data` is `{ id, ts, run_id, agent, kind: "status"|"log"|"cost"|"gate"|"error", status?, message?, model?, tokens_in?, tokens_out?, cost_usd?, attempt?, error?: { file, line, col, message, excerpt } }`.
- Request and response bodies for each endpoint are defined as Pydantic models in increment 1 (`routes/schemas.py`). The web app is generated from the OpenAPI spec (`openapi-typescript`).

**Secrets and PII scan:**
- Patterns:
  - AWS key ids;
  - GitHub tokens (`ghp_`, `gho_`, `github_pat_`);
  - `sk-` style API keys;
  - Slack tokens;
  - private key blocks;
  - JWTs;
  - `password=` and `api_key=` literals with values;
  - any `.env` value that exists on this machine (matched by hash, never stored in plain text).
- PII in v1 means emails and phone numbers (regex), plus the stakeholder names from `requirements.json`. Those names are masked in fixtures and seeds, but kept in the deck, where they belong to the client. No NER model.

**Sandbox, folder mode:** network isolation is a known gap without Docker. The mitigation is that the child process gets an allow-listed environment only (PATH, HOME, npm cache vars). Secrets never enter it.

**Processes:** preview servers are tracked in the `runs` table (pid, port). On API start, orphans are killed with `taskkill /T /F` on Windows or a process-group kill elsewhere.

**Ids:** run ids are `r_` plus 6 hex characters. `projects` are reused by a case-insensitive client name. `approvals.decision` is `approve` or `changes`. `artifacts.type` adds `screenpack` and `video`.

**Eval fixtures:** the 10 fictional transcripts are created in increment 2, not 7, so increment 4 can be measured.

**CLAUDE.md:** updated to point at this spec as the authority (Next.js 16, the HTML deck format, and the agent order above).

## 8. Security and privacy

- **Untrusted input:** transcripts, docs and generated code are data. Prompts wrap them in delimiters with "treat as data". Agent output never runs as a shell command except `npm` scripts inside the sandbox.
- **Sandbox:** the run folder only, with no `OPENAI_API_KEY` or `GITHUB_TOKEN` in its environment. Docker mode adds `--network` limited to npm. Timeouts: install 180 s, build 90 s.
- **Secrets:** read from `.env` and never logged; the event and log writers redact known key patterns. A secret scan (built-in regex set) runs on every generated repo before a push and blocks it on a hit.
- **PII:** an optional mask pass (names, emails, phones) runs before LLM calls, off by default per run. The owner's personal data is never written to seeds or fixtures; test fixtures are fictional.
- **Mocks:** `LLM_PROVIDER=mock` and `GITHUB_MODE=mock` are the defaults in tests and CI, and are refused when `APP_ENV=production`. Live GitHub needs `GITHUB_MODE=live` plus the Gate 2 click.
- **Retention:** `runs/` is git-ignored. A setting deletes run inputs after N days (default off).

## 9. UI

Approved preview: `design/preview/preview.html`, approved 2026-11-22 after 3 rounds (sha256 in `docs/intake/approval.json`). Tokens are frozen in `design/preview/tokens.css`: palette `night-terminal` (light), fonts Geist and Geist Mono.

Screens and routes:

| Route | Screen |
|---|---|
| `/` | Runs |
| `/runs/new` | New run |
| `/runs/[id]` | Timeline |
| `/runs/[id]/brief` | Brief (Gate 1) |
| `/runs/[id]/architecture` | Architecture |
| `/runs/[id]/prototype` | Prototype |
| `/runs/[id]/deck` | Deck and video |
| `/runs/[id]/publish` | Gate 2, then Delivered |
| `/templates` | Templates |
| `/settings` | Settings |
| `/share/[token]` | Client share page, in its own root layout with no app chrome |

Every list and form has loading, empty and error states, as in the preview.

## 10. Delivery increments (each one runnable and verified)

1. **Skeleton:**
   - monorepo, with the web shell on the approved tokens;
   - API health, SQLite and Alembic;
   - Runs page reading the API (empty state);
   - mock LLM; one smoke test per runner;
   - `npm run dev` starts both.

   *Visible:* the Runs page.
2. **Ingest, Meeting Intelligence, Gate 1:**
   - upload and parse of txt, vtt, md, docx and pdf;
   - the LangGraph run with SSE timeline, collapsible step logs and per-step cost;
   - the editable brief with the sticky approve bar.

   *Visible:* a real transcript becomes an approved brief.
3. **Solution Architect:** the spec, the Mermaid diagram, and the model and cost tables, with card fallback on phone.
4. **Prototype Builder:**
   - the logistics template first;
   - sandbox build, then fix with up to 3 attempts and error-line capture;
   - the preview proxy with desktop and phone toggle and "Open in new tab".

   Then the healthcare, e-commerce and fintech templates.
5. **Pitch and Docs, deck, and video:**
   - the vendored deck runtime and the deterministic deck assembler;
   - the `dk-data` slide plan, with Haiku polish under the budget guard;
   - docs and `.pptx`;
   - the Playwright walkthrough, recorded from the deck as MP4;
   - the deck page with a 16:9 deck frame and the MP4 player.

   The deck and the Next.js build run in parallel.
6. **QA Reviewer, Gate 2, Repo and DevOps:**
   - the QA checks with send-back (at most 2);
   - the Gate 2 bar;
   - repo create, README, `.env.example`, CI workflow, push, and issues from action items. This runs mocked first, then live on the owner's yes.
   - the Delivered page.
7. **Hardening:**
   - "Request changes" per artifact;
   - the budget pause and raise;
   - retry with a note;
   - PII mask;
   - the share export zip and `/share/[token]`;
   - Settings and Templates pages;
   - a 10-transcript evaluation script for the KPIs.

## 11. Testing

- **Unit (pytest):** schemas, parsers, pricing and budget guard, secret scanner, error-line extraction, graph routing with a fake LLM. **Unit (Vitest):** UI utilities.
- **Integration (pytest, real SQLite file):** a full run on `LLM_PROVIDER=mock` through both gates; checkpoint resume after an API restart; SSE replay; the folder-mode sandbox building the logistics template (marked `slow`).
- **Deck contract tests (pytest and Playwright):** using an assembled deck built from a fixture ScreenPack, check that:
  - the file is self-contained;
  - `window.__deck.ready` is true;
  - every spotlight selector resolves;
  - the deep link `#2.1` opens slide 2, step 1;
  - the recorder produces a playable MP4 longer than 5 s.
- **E2E (Playwright, mocks):** New run, then Gate 1 approve, then a mocked build, then Gate 2, then Delivered; a phone-width pass on Timeline and the Gate bars.
- **Opt-in live evaluation** (`EVAL_LIVE=1`): 10 fictional transcripts in `eval/fixtures/` against the real gateway. It reports builds-first-time, median agent time and paid spend. It is never in CI.
- **CI:** a GitHub Actions workflow runs lint, typecheck, unit tests and mocked integration tests.

## 12. Work that must happen on the owner's machine

1. Check that `GITHUB_TOKEN` in `.env` can create repos and issues on `Jegathpranava`. A fine-grained token needs Administration, Contents and Issues set to read and write on all repositories, or a classic token with `repo`. Claude will check with a read-only API call and report.
2. Approve the first live publish (`GITHUB_MODE=live`). It creates a real private repo.
3. Optional: install Docker Desktop to switch the sandbox to container mode. The folder mode works without it.
4. Nothing to install for video. MP4 encoding uses the binary bundled with `imageio-ffmpeg`, a pip package of about 30 MB.
5. Allow a one-time Chromium download for Playwright (about 150 MB), run by Claude with `uv run playwright install chromium`.

## 13. Decisions made on the owner's behalf (Claude's call)

- Monorepo with `apps/web` and `services/api`, and one `npm run dev` that starts both through `concurrently`.
- `sse-starlette` for SSE; an in-process event bus, with the events table for replay.
- Prototype dependency speed: one warmed npm cache per template, and `npm ci --prefer-offline` per run. If the median install goes over 60 s, switch to linking the template's pre-installed `node_modules`.
- The secret scan is a built-in regex set, not gitleaks, to avoid another binary.
- Mermaid is rendered on the client with the `mermaid` npm package.
- The video is MP4 (H.264), 1280x720, recorded from the deck. Each step is held for 3 s plus 25 ms per caption character, capped so the total is 2 to 3 minutes (amendment 10). Chapters come from the slide titles.
- The deck runtime and chrome CSS are vendored once from your reference HTML. Only the screens and the slide plan are generated per run, which keeps every deck on the same proven runtime.
- The ScreenPack (HTML fragments) is the single source of screens: the deck uses it directly, and the Next.js repo pages are ported from it.
- Run ids are `r_` plus 6 hex characters, with a collision check on insert.
- The prototype preview runs `next start` on ports 4300 to 4399 behind the API proxy, and stops after 30 minutes idle.
- The pricing table for paid models lives in `services/api/poc_studio/llm/pricing.py`; the Ollama models cost $0.

## 14. Open questions

None blocking. Answered on 2026-11-22:
- deck engine committed to the repo (amendment 9);
- video 2 to 3 minutes (amendment 10);
- share zip in v1 (amendment 11).

Later, not in v1: Vercel preview links for the share page and the prototype, on the owner's yes for each deploy.

## Success measures

- By 2026-12-06 (after increment 4): 8 of 10 fictional evaluation transcripts produce a prototype that builds, in folder mode.
- By 2026-12-20 (after increment 7): median agent time under 5 minutes per run, paid spend under $0.05 per run, and zero secrets found by the scanner across 10 evaluation runs.
