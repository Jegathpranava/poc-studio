# Eval

KPI runs over the 10 fixtures in `eval/fixtures/` (expected sectors and must-have features in `expected.json`).
Run from `services/api`.

```
uv run python ../../eval/run_eval.py --stage build --dry
EVAL_LIVE=1 uv run python ../../eval/run_eval.py --stage build
uv run python ../../eval/run_eval.py --stage build --dry --only logistics-02-harbourline-warehouse-brd.md
```

Options: `--only <file>` (repeatable), `--out <path>` (default `eval/report-build.md`).

- Dry: mock provider, fake npm install and build, no network, seconds. The mock quotes `tests/ingest/fixtures/sample.vtt`, so that file is uploaded in place of each fixture. Exit code is always 0.
  Sector and feature scores show "n/a (mock)" because the mock returns the same output for every fixture.
- Live: refuses without `EVAL_LIVE=1`. Calls the gateway and npm; expected paid spend under $0.50.
  Exit code is 1 if fewer than 8 of 10 build.
- Each fixture runs in its own temp DB and runs dir through the real app (TestClient). Gate 1 is auto-approved (eval mode only).
- Agent time = wall clock from run start to `waiting_gate2`, minus the time held at Gate 1.
- Features found = must-haves matched case-insensitively against feature names and details
  (full substring, or at least 60% of the must-have's key words inside one feature).
