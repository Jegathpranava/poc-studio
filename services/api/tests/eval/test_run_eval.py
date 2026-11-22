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


FULL_ONLY = ["logistics-01-northgate-freight-discovery.vtt", "healthcare-02-brightpath-intake-brd.md"]


def test_dry_full_stage_two_fixtures(tmp_path: Path, restore_env: None) -> None:
    mod = _load()
    out = tmp_path / "full.md"
    report, code = mod.run_eval("full", dry=True, only=FULL_ONLY, out=out)
    assert code == 0
    assert out.read_text(encoding="utf-8") == report
    rows = [ln for ln in report.splitlines() if ln.startswith("| ") and ("vtt" in ln or ".md" in ln)]
    assert len(rows) == 2
    assert all("| delivered |" in r for r in rows)
    assert "- PASS: Builds total: 2/2" in report
    assert "- PASS: Secret findings: 0 across 2 runs" in report
    for label in ("Builds total", "Median agent time", "Max paid per run", "Secret findings"):
        assert any(f"{m}: {label}" in report for m in ("PASS", "FAIL"))
    assert "Delivered: 2/2" in report and "Decks: 2/2" in report and "Videos: 2/2" in report


def test_measures_fail_on_secrets_slow_runs_and_spend() -> None:
    mod = _load()
    ok = mod.Row(file="a", build_ok=True, agent_time_s=10.0, paid_usd=0.01)
    bad = mod.Row(file="b", build_ok=False, agent_time_s=400.0, paid_usd=0.06, secret_findings=1)
    verdict = {label: passed for label, passed, _ in mod.measures([ok, bad, bad])}
    assert verdict == {
        "Builds total": False,
        "Median agent time": False,
        "Max paid per run": False,
        "Secret findings": False,
    }
    assert all(p for _, p, _ in mod.measures([ok] * 10))


def test_full_live_is_refused_without_the_flag(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EVAL_LIVE", raising=False)
    mod = _load()
    with pytest.raises(mod.LiveRefused):
        mod.run_eval("full", dry=False)
    assert mod.main(["--stage", "full"]) == 2


def test_github_is_forced_to_mock_and_video_to_fake_even_when_live(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, restore_env: None
) -> None:
    import os

    from poc_studio.config import get_settings

    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("GITHUB_MODE", "live")
    monkeypatch.delenv("VIDEO_FAKE", raising=False)
    get_settings.cache_clear()
    mod = _load()
    with mod._isolated(dry=False):  # live mode, as `EVAL_LIVE=1` would run it
        assert os.environ["GITHUB_MODE"] == "mock"
        assert os.environ["VIDEO_FAKE"] == "1"
        assert get_settings().github_mode == "mock"
    assert os.environ["GITHUB_MODE"] == "live"
    assert "VIDEO_FAKE" not in os.environ
    with mod._isolated(dry=False, real_video=True):
        assert "VIDEO_FAKE" not in os.environ
    # and a whole run with the env saying live still publishes to the mock and is restored afterwards
    report, _ = mod.run_eval("full", dry=True, only=FULL_ONLY[:1], out=tmp_path / "r.md")
    assert "| delivered |" in report
    assert os.environ["GITHUB_MODE"] == "live"
    get_settings.cache_clear()
