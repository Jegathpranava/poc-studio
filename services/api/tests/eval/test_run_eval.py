import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[4] / "eval" / "run_eval.py"


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("run_eval", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["run_eval"] = mod  # dataclasses look the module up by name
    spec.loader.exec_module(mod)
    return mod


def test_score_features_substring_and_keywords() -> None:
    mod = _load()
    feats = [{"name": "Delivery window risk board", "detail": "shows predicted arrival per shipment"}]
    must = ["delivery window risk board with predicted arrival", "Unrelated payroll export"]
    assert mod.score_features(must, feats) == 1


@pytest.fixture
def restore_env(monkeypatch: pytest.MonkeyPatch):  # noqa: ANN201
    # run_eval switches the DB and runs dir through env vars; restore the suite's values afterwards.
    from poc_studio.config import get_settings
    from poc_studio.db import session as db_session

    for key in ("POC_DATABASE_URL", "RUNS_DIR", "LLM_PROVIDER", "GITHUB_MODE", "APP_ENV"):
        monkeypatch.setenv(key, "placeholder")  # the undo below restores the original (or removes it)
    yield
    monkeypatch.undo()
    get_settings.cache_clear()
    db_session.get_engine.cache_clear()
    db_session._factory.cache_clear()


def test_dry_eval_two_fixtures(tmp_path: Path, restore_env: None) -> None:
    mod = _load()
    only = ["logistics-01-northgate-freight-discovery.vtt", "healthcare-02-brightpath-intake-brd.md"]
    out = tmp_path / "report.md"
    report, code = mod.run_eval("build", dry=True, only=only, out=out)
    assert code == 0
    assert out.read_text(encoding="utf-8") == report
    rows = [ln for ln in report.splitlines() if ln.startswith("| ") and ("vtt" in ln or ".md" in ln)]
    assert len(rows) == 2
    assert all("| yes |" in r for r in rows)
    assert "**Summary:**" in report and "builds total 2/2" in report
    assert "n/a (mock)" in report


def test_dry_eval_restores_the_env_and_the_runner(tmp_path: Path, restore_env: None) -> None:
    import os

    from poc_studio.sandbox import runner

    mod = _load()
    before_env = dict(os.environ)
    before_fns = (runner.install, runner.build)
    only = ["logistics-01-northgate-freight-discovery.vtt"]
    mod.run_eval("build", dry=True, only=only, out=tmp_path / "r.md")
    assert dict(os.environ) == before_env
    assert (runner.install, runner.build) == before_fns


def test_live_is_refused_inside_run_eval_without_the_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_LIVE", raising=False)
    mod = _load()
    with pytest.raises(mod.LiveRefused):
        mod.run_eval("build", dry=False)
    assert mod.main(["--stage", "build"]) == 2
