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
