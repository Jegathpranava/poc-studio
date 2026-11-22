from datetime import timedelta

from poc_studio.config import get_settings
from poc_studio.db.models import now
from poc_studio.retention import apply_retention
from tests.share.conftest import run_dir, seed_run


def _with_input(run_id: str) -> None:
    (run_dir(run_id) / "input").mkdir(parents=True, exist_ok=True)
    (run_dir(run_id) / "input" / "call.vtt").write_text("WEBVTT", encoding="utf-8")


def test_old_inputs_are_deleted_and_artifacts_kept(env, monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "retention_days", 1)
    old = seed_run(started_at=now() - timedelta(days=3))
    fresh = seed_run(started_at=now() - timedelta(hours=2))
    _with_input(old)
    _with_input(fresh)
    assert apply_retention(get_settings()) == 1
    assert not (run_dir(old) / "input").exists()
    assert (run_dir(old) / "requirements.v1.json").is_file()  # artifacts stay
    assert (run_dir(old) / "deck").is_dir()
    assert (run_dir(fresh) / "input" / "call.vtt").is_file()
    assert apply_retention(get_settings()) == 0  # nothing left to delete


def test_zero_days_turns_it_off(env, monkeypatch) -> None:
    monkeypatch.setattr(get_settings(), "retention_days", 0)
    old = seed_run(started_at=now() - timedelta(days=400))
    _with_input(old)
    assert apply_retention(get_settings()) == 0
    assert (run_dir(old) / "input").is_dir()


def test_default_is_off_and_startup_deletes_nothing(client, env) -> None:
    from poc_studio.extra_routes import on_startup

    assert client.get("/api/settings").json()["retention_days"] == 0
    old = seed_run(started_at=now() - timedelta(days=400))
    _with_input(old)
    assert on_startup() == 0
    assert (run_dir(old) / "input").is_dir()
