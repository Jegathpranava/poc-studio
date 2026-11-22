# Decisions

Resolved values, recorded by Task 1. The design spec (`docs/specs/2026-11-22-poc-studio-design.md`) stays the authority.

## Resolved values

| Topic | Value |
|---|---|
| Run id | `r_` plus 6 hex characters (for example `r_3fa91c`) |
| Deck length | 9 to 12 slides (welcome, optional overview, area slides, play, close) |
| ScreenPack | 6 to 12 screens, 3 to 8 anchors per screen |
| Area slide steps | 3 to 5 |
| Next.js build timeout | 90 s |
| npm install timeout | 180 s |
| LLM call timeout | 90 s, with 2 JSON repair retries |
| Video length | 120 to 180 s, with the hands-on (play) slide skipped |
| Run budget | $0.05 per run, $5 per month |
| Mock switches | `LLM_PROVIDER=mock` and `GITHUB_MODE=mock` are the test defaults and are refused when `APP_ENV=production` |
| Database | `data/poc-studio.sqlite` at the repo root (git-ignored) |

## Task 1 notes

- The API reads its database location from `POC_DATABASE_URL`, not `DATABASE_URL`. The repo-root `.env` may hold an older `DATABASE_URL` value, and the owner's `.env` is never edited, so the old name is ignored.
- Settings are read from the repo-root `.env` and the process environment. Secrets are held as `SecretStr`.

## Verified prices

Appended by Task 4.

## LLM pricing

Task 4. Constants live in `services/api/poc_studio/llm/pricing.py`. Prices are USD per 1M tokens (input / output).

| Model | Input | Output | Status |
|---|---|---|---|
| `fast`, `smart`, `vision`, `embed`, `guard` | 0 | 0 | Free gateway models |
| `claude-haiku-5-5` | 0.10 | 0.50 | VERIFY_PRICE: from the claude-api skill table (cached 2026-11-03), list price for prompts up to 100K tokens |
| `claude-sonnet-5-5` | 2.00 | 10.00 | VERIFY_PRICE: same source |
| `claude-opus-5-5` | 4.00 | 20.00 | VERIFY_PRICE: same source |

These are Anthropic first-party list prices. The gateway's own billing is not confirmed. The owner-only live test (`EVAL_LIVE=1`) must compare them with the gateway usage before they count as verified. Haiku input is capped at 12,000 tokens (`InputTooLarge`).

## GitHub publish

Task 18.
- The token reaches git through `GIT_CONFIG_COUNT/KEY_0/VALUE_0` (`http.extraheader`) in the child process environment: same effect as `git -c`, but it is not on a command line, in `.git/config` or in the remote URL.
- The first commit author is `PoC Studio <noreply@example.com>`, never the owner's address.
- Mock mode inits and commits locally in `runs/<id>/publish/` and records the planned calls in `runs/<id>/publish.mock.json`. It never adds a remote or pushes.
- A name clash gets `-2`, `-3` and so on. A blocked publish (secret scan or QA `block_publish`) fails the repo step and the run ends `failed`; there is no `delivered` without a repo URL.
- The secret scan no longer hashes `.env` values of non-credential settings (`*_MODEL`, `*_BASE_URL`, `*_MODE` and similar): a public model name in a generated README was a false positive.
- Migration 0005 adds the `repo` artifact type.

## Request changes, retry and budget

Task 19. Routes in `services/api/poc_studio/routes/revise.py`; request and response models live there, not in `routes/schemas.py`.
- Revisions are allowed only while the run waits at Gate 2 (the brief only at Gate 1, as a Gate 1 "changes"). Any other state is a 409.
- `POST /api/runs/{id}/artifacts/{architecture|prototype|deck|brief}/revise {note}` records a Gate 2 decision "changes" with `edits = {"revise": <agent>}` and the note. Owners: architecture is `architect`, prototype is `screens`, deck is `pitch`. The Approval row keeps it, so it survives a restart.
- The gate2 node writes `revise_note = {agent: note}` into the state, and `after_gate2` routes to the agent (`pitch` goes through `pitch_retry`). The normal edges then run what follows it, ending at Gate 2 again. "Changes" without `revise` still waits at the gate.
- Each owning agent adds the note to its prompt and clears it in its own state update; only that agent writes the key, so the parallel pitch and port branches never write it together. A rerun makes version N+1 of its artifact. The `deck` type shares one version counter with the assembled html, so the second plan file can be `plan.v3.json`.
- `POST /api/runs/{id}/retry {note?, attempts?: 1..3 = 3}`:
  - a run at Gate 2 whose `build_result.ok` is false reruns `port_retry` with a fresh attempt budget (`port_attempts`), the note going into the PortFix prompt, then assemble, QA and Gate 2;
  - a `failed` run resumes from its checkpoint (`RunService.resume(..., allow_failed=True)`; the note is ignored);
  - anything else is a 409.
- `POST /api/runs/{id}/budget {budget_usd?, use_free_model?}` for a `paused_budget` run. `budget_usd` must be above `paid_usd` and at most $1.00 (422 otherwise); sending neither field is a 422. A raise goes through `RunService.resume`, which also writes `limit_usd` to the checkpoint. `use_free_model` sets the state flag `free_polish`: the pitch step skips Haiku and keeps its drafted titles and captions (the flag stays for later deck revisions). The pause happens before the paid call, so the resumed run never makes a duplicate paid call.
- UI: `RunBudgetBanner` is mounted once in the run frame, so it shows on every run page including the timeline. Request changes buttons are enabled only at Gate 2. The failed-step buttons show for a failed port at Gate 2 and Resume for a `failed` run.
