"""KPI evaluation over the 10 fixtures, through the real FastAPI app in-process.

Run from services/api:  uv run python ../../eval/run_eval.py --stage build [--dry] [--only FILE] [--out PATH]

Stages: `build` (this file). Task 21 adds `full` by registering a runner in STAGES.
Gates are auto-approved here (eval mode only).
"""

from __future__ import annotations

import argparse
import contextlib
import json
import os
import statistics
import sys
import tempfile
import time
from collections.abc import Callable, Iterator
from dataclasses import dataclass
from pathlib import Path
from typing import Any

EVAL_DIR = Path(__file__).resolve().parent
API_DIR = EVAL_DIR.parent / "services" / "api"
if str(API_DIR) not in sys.path:  # `python eval/run_eval.py` puts only eval/ on the path
    sys.path.insert(0, str(API_DIR))
FIXTURES = EVAL_DIR / "fixtures"
RUN_TIMEOUT_S = 600.0
POLL_S = 0.1
TERMINAL = {"waiting_gate2", "failed", "paused_budget"}
MIN_BUILDS = 8
LIVE_WARNING = "Live eval calls the gateway and npm; expected paid spend under $0.50"
MOCK_NA = "n/a (mock)"
# The mock provider's canned requirements quote this transcript, and Gate 0 drops quotes not found in the
# upload, so dry runs upload it in place of the fixture (the real parsers are covered by their own tests).
MOCK_TRANSCRIPT = API_DIR / "tests" / "ingest" / "fixtures" / "sample.vtt"


@dataclass
class Row:
    file: str
    status: str = "unknown"
    sector_ok: bool | None = None
    features_found: int | None = None
    features_total: int = 3
    build_ok: bool = False
    attempt: int | None = None
    agent_time_s: float | None = None
    paid_usd: float = 0.0
    tokens: int = 0
    error: str | None = None


# ---- scoring (pure) --------------------------------------------------------------------------


def _words(text: str) -> set[str]:
    cleaned = "".join(c.lower() if c.isalnum() else " " for c in text)
    return {w for w in cleaned.split() if len(w) > 3}


def feature_found(must_have: str, features: list[dict[str, Any]]) -> bool:
    """Case-insensitive substring over feature names and details; else most key words in one feature."""
    needle = must_have.lower()
    texts = [f"{f.get('name', '')} {f.get('detail', '')}".lower() for f in features]
    if any(needle in t for t in texts):
        return True
    want = _words(must_have)
    return bool(want) and any(len(want & _words(t)) / len(want) >= 0.6 for t in texts)


def score_features(must_haves: list[str], features: list[dict[str, Any]]) -> int:
    return sum(feature_found(m, features) for m in must_haves)


# ---- one fixture -----------------------------------------------------------------------------


def client_name_from(file: str) -> str:
    parts = Path(file).stem.split("-", 2)
    slug = parts[2] if len(parts) == 3 else Path(file).stem
    return " ".join(w.capitalize() for w in slug.split("-"))


def _wait(client: Any, run_id: str, wanted: set[str], deadline: float) -> dict[str, Any]:
    body: dict[str, Any] = {}
    while time.monotonic() < deadline:
        body = client.get(f"/api/runs/{run_id}").json()
        if body["status"] in wanted:
            return body
        time.sleep(POLL_S)
    raise TimeoutError(f"run stayed {body.get('status')!r}, wanted one of {sorted(wanted)}")


def _clear_caches() -> None:
    from poc_studio.config import get_settings
    from poc_studio.db import session as db_session

    get_settings.cache_clear()
    db_session.get_engine.cache_clear()
    db_session._factory.cache_clear()


def _patch_sandbox() -> None:
    """Same fakes as tests/conftest.py, applied inside this process (undone by `_isolated`)."""
    from poc_studio.sandbox import runner

    async def fake_install(app_dir):  # noqa: ANN001, ANN202
        return runner.StepResult(ok=True, duration_s=0.0)

    async def fake_build(app_dir, attempt=1):  # noqa: ANN001, ANN202
        return runner.BuildResult(ok=True, duration_s=0.0, attempt=attempt)

    runner.install = fake_install
    runner.build = fake_build


@contextlib.contextmanager
def _isolated(dry: bool) -> Iterator[None]:
    """Env changes and the dry sandbox fakes last for one eval and are undone afterwards, also on errors."""
    saved_env = dict(os.environ)
    saved_fns: tuple[Any, Any] | None = None
    if dry:
        from poc_studio.sandbox import runner

        saved_fns = (runner.install, runner.build)
    try:
        configure_env(dry)
        if dry:
            _patch_sandbox()
        yield
    finally:
        if saved_fns is not None:
            from poc_studio.sandbox import runner

            runner.install, runner.build = saved_fns
        os.environ.clear()
        os.environ.update(saved_env)
        if "poc_studio.config" in sys.modules:
            _clear_caches()  # settings were read from the eval's env: drop them


def run_fixture(entry: dict[str, Any], dry: bool) -> Row:
    from fastapi.testclient import TestClient

    from poc_studio.db import models  # noqa: F401
    from poc_studio.db.base import Base
    from poc_studio.db.session import get_engine
    from poc_studio.main import create_app

    row = Row(file=entry["file"], features_total=len(entry["must_have_features"]))
    path = MOCK_TRANSCRIPT if dry and MOCK_TRANSCRIPT.is_file() else FIXTURES / entry["file"]
    with tempfile.TemporaryDirectory(prefix="poc-eval-", ignore_cleanup_errors=True) as tmp:
        tmp_path = Path(tmp)
        os.environ["POC_DATABASE_URL"] = f"sqlite:///{(tmp_path / 'app.sqlite').as_posix()}"
        os.environ["RUNS_DIR"] = str(tmp_path / "runs")
        _clear_caches()
        Base.metadata.create_all(get_engine())
        try:
            with TestClient(create_app()) as client:
                started = time.monotonic()
                deadline = started + RUN_TIMEOUT_S
                res = client.post(
                    "/api/runs",
                    files=[("files", (path.name, path.read_bytes(), "application/octet-stream"))],
                    data={"client": client_name_from(entry["file"]), "sector": entry["sector"]},
                )
                res.raise_for_status()
                run_id = res.json()["id"]
                at_gate1 = _wait(client, run_id, {"waiting_gate1", "failed", "paused_budget"}, deadline)
                if at_gate1["status"] == "waiting_gate1":
                    gate1_seen = time.monotonic()
                    approve = client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
                    approve.raise_for_status()
                    gate1_s = time.monotonic() - gate1_seen  # time held at Gate 1 is not agent time
                    final = _wait(client, run_id, TERMINAL, deadline)
                else:
                    gate1_s, final = 0.0, at_gate1
                row.agent_time_s = time.monotonic() - started - gate1_s
                row.status = final["status"]
                row.paid_usd = float(final.get("paid_usd") or 0.0)
                row.tokens = int(final.get("tokens_total") or 0)
                _score(row, entry, run_id, dry)
        except Exception as exc:  # one bad fixture must not stop the other nine
            if row.status == "unknown":
                row.status = "error"
            row.error = f"{type(exc).__name__}: {exc}"
        finally:
            get_engine().dispose()
            _clear_caches()
    return row


def _score(row: Row, entry: dict[str, Any], run_id: str, dry: bool) -> None:
    from poc_studio.config import get_settings
    from poc_studio.runs.edits import load_latest_requirements

    build_file = get_settings().runs_dir / run_id / "build.json"
    if build_file.is_file():
        info = json.loads(build_file.read_text(encoding="utf-8"))
        row.build_ok = bool(info.get("ok"))
        row.attempt = info.get("attempts") or info.get("attempt")
    req = load_latest_requirements(run_id)
    if req is not None and not dry:  # mock output is identical for every fixture, so these would mislead
        row.sector_ok = req.sector == entry["sector"]
        row.features_found = score_features(
            entry["must_have_features"], [f.model_dump() for f in req.features]
        )


# ---- report ----------------------------------------------------------------------------------


def _fmt_time(seconds: float | None) -> str:
    return "-" if seconds is None else f"{seconds:.1f}s"


def render_report(rows: list[Row], dry: bool, stage: str = "build") -> str:
    mode = "dry (mock provider, fake npm)" if dry else "live"
    lines = [
        f"# Eval report: stage `{stage}`, {mode}",
        "",
        "| file | sector ok | features found/3 | build ok | attempt | agent time | paid $ |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        if dry:
            sector, feats = MOCK_NA, MOCK_NA
        else:
            sector = "-" if r.sector_ok is None else ("yes" if r.sector_ok else "no")
            feats = "-" if r.features_found is None else f"{r.features_found}/{r.features_total}"
        build = "yes" if r.build_ok else f"no ({r.status})"
        attempt = "-" if r.attempt is None else str(r.attempt)
        lines.append(
            f"| {r.file} | {sector} | {feats} | {build} | {attempt} | {_fmt_time(r.agent_time_s)} "
            f"| {r.paid_usd:.4f} |"
        )
    n = len(rows)
    first = sum(1 for r in rows if r.build_ok and r.attempt == 1)
    total_ok = sum(1 for r in rows if r.build_ok)
    times = [r.agent_time_s for r in rows if r.agent_time_s is not None]
    med = statistics.median(times) if times else None
    paid = sum(r.paid_usd for r in rows)
    mean = paid / n if n else 0.0
    lines += [
        "",
        f"**Summary:** builds first time {first}/{n}; builds total {total_ok}/{n}; "
        f"median agent time {_fmt_time(med)}; paid total ${paid:.4f}, mean ${mean:.4f} per run.",
    ]
    if dry:
        lines.append("Sector and feature scores are not meaningful with the mock provider.")
    errors = [f"- {r.file}: {r.error}" for r in rows if r.error]
    if errors:
        lines += ["", "Errors:", *errors]
    return "\n".join(lines) + "\n"


# ---- stages and CLI --------------------------------------------------------------------------


def load_expected(only: list[str] | None) -> list[dict[str, Any]]:
    entries = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))
    if only:
        entries = [e for e in entries if e["file"] in only or Path(e["file"]).stem in only]
        if not entries:
            raise SystemExit(f"--only matched no fixture: {only}")
    return entries


def run_build_stage(entries: list[dict[str, Any]], dry: bool) -> list[Row]:
    return [run_fixture(e, dry) for e in entries]


STAGES: dict[str, Callable[[list[dict[str, Any]], bool], list[Row]]] = {"build": run_build_stage}


class LiveRefused(RuntimeError):
    """A live (paid) eval was asked for without EVAL_LIVE=1."""


def configure_env(dry: bool) -> None:
    """Must run before poc_studio settings are first read."""
    if dry:
        os.environ["LLM_PROVIDER"] = "mock"
        os.environ["GITHUB_MODE"] = "mock"
        os.environ["APP_ENV"] = "test"
    os.environ.setdefault("GITHUB_MODE", "mock")  # the eval never publishes


def run_eval(
    stage: str, dry: bool, only: list[str] | None = None, out: Path | None = None
) -> tuple[str, int]:
    """Returns (report, exit_code). Raises LiveRefused for a live run without EVAL_LIVE=1."""
    if stage not in STAGES:
        raise SystemExit(f"unknown stage {stage!r}; available: {', '.join(STAGES)}")
    if not dry and os.environ.get("EVAL_LIVE") != "1":
        raise LiveRefused("Refusing to run live: set EVAL_LIVE=1 (or use --dry).")
    with _isolated(dry):
        rows = STAGES[stage](load_expected(only), dry)
    report = render_report(rows, dry, stage)
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(report, encoding="utf-8")
    built = sum(1 for r in rows if r.build_ok)
    return report, 0 if dry or built >= MIN_BUILDS else 1


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="PoC Studio KPI evaluation")
    p.add_argument("--stage", choices=sorted(STAGES), default="build")
    p.add_argument("--dry", action="store_true", help="mock provider, fake npm, no network")
    p.add_argument("--only", action="append", help="fixture file name (repeatable)")
    p.add_argument("--out", type=Path, default=None, help="report path (default eval/report-<stage>.md)")
    args = p.parse_args(argv)
    if not args.dry and os.environ.get("EVAL_LIVE") == "1":
        print(f"WARNING: {LIVE_WARNING}.", file=sys.stderr)
    out = args.out or (EVAL_DIR / f"report-{args.stage}.md")
    try:
        report, code = run_eval(args.stage, args.dry, args.only, out)
    except LiveRefused as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(report)
    return code


if __name__ == "__main__":
    sys.exit(main())
