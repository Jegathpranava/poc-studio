# Eval

KPI runs over the 10 fixtures in `eval/fixtures/` (expected sectors and must-have features in `expected.json`).
Run from `services/api`.

## Stages

- `build`: upload, auto-approve Gate 1, stop at Gate 2. Measures sector, features, build and agent time.
- `full`: upload, Gate 1 approved, Gate 2 approved with default options, then wait for `delivered` or `failed`
  (15 minutes per fixture). Publish is always mocked. Measures everything in `build` plus QA counts, secret
  findings, deck, video, total time and paid spend, and checks the success measures from the design spec.

```
uv run python ../../eval/run_eval.py --stage build --dry
uv run python ../../eval/run_eval.py --stage full --dry
uv run python ../../eval/run_eval.py --stage full --dry --only logistics-02-harbourline-warehouse-brd.md
```

Owner-only live commands (they call the gateway and npm; expected paid spend under $0.50 in total, Haiku polish only):

```
EVAL_LIVE=1 uv run python ../../eval/run_eval.py --stage build
EVAL_LIVE=1 uv run python ../../eval/run_eval.py --stage full
EVAL_LIVE=1 uv run python ../../eval/run_eval.py --stage full --real-video   # adds 2 to 3 minutes per run
```

## Flags

- `--stage build|full` (default `build`).
- `--dry`: mock provider, fake npm, no network.
- `--only <file>` (repeatable): run a subset. The builds threshold scales to 80% of the rows run.
- `--out <path>`: report path (default `eval/report-<stage>.md`; these files are scratch output, do not commit them).
- `--real-video`: record the real walkthrough. Off by default: the eval sets `VIDEO_FAKE=1` (a 2 s clip) because a
  real recording takes 2 to 3 minutes per run.

## Dry mode

Mock provider, fake npm install and build, no network, about 25 seconds for all 10. The mock quotes
`tests/ingest/fixtures/sample.vtt`, so that file is uploaded in place of each fixture. Exit code is always 0.

What dry proves: the whole graph runs end to end through the real app for every fixture, both gates, QA, deck and
video artifacts, the mock publish, report rendering and the PASS/FAIL logic.

What dry does not prove: extraction quality (sector and feature scores show "n/a (mock)" because the mock returns
the same output for every fixture), real `npm ci` and `next build` success, real agent time, real model cost
(paid spend is always 0), or a real video recording.

## Live mode

Refuses without `EVAL_LIVE=1` (exit 2) and prints the cost warning. Uses the real gateway models (fast, smart,
Haiku polish) and real npm. `GITHUB_MODE` is forced to `mock` inside the eval even if `.env` says live: the eval
never publishes to GitHub. The `full` stage exits 1 if any success measure FAILs; `build` exits 1 if fewer than
8 of 10 build.

## Isolation

Each fixture runs in its own temp DB and runs dir through the real app (TestClient). Gates are auto-approved
(eval mode only). Env changes and the dry sandbox fakes are undone afterwards.

## Measures

- Agent time (spec 7b) = wall clock from run start to `waiting_gate2`, minus the time held at Gate 1.
- Total time = run start to `delivered` (`full` only).
- Features found = must-haves matched case-insensitively against feature names and details
  (full substring, or at least 60% of the must-have's key words inside one feature). Live only.
- QA passed/failed = counts from the latest `qa_report`.
- Secret findings = 1 per run where the latest QA report fails `no_secrets` or sets `block_publish`. A blocked
  publish leaves the run at Gate 2 and is reported as an error.
- Deck = a `deck` artifact exists; video = an MP4 `video` artifact exists.

## Success measures (full summary)

| measure | pass when |
|---|---|
| Builds total | at least 8 of 10 |
| Median agent time | under 300 s |
| Max paid per run | under $0.05 |
| Secret findings | 0 across all runs |

Delivered, decks and videos are reported as counts out of the rows run.
