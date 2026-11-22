from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select

from poc_studio.db.models import AgentStep, Artifact
from poc_studio.db.session import open_session
from poc_studio.events import load_events
from poc_studio.llm.client import set_provider
from poc_studio.media import video
from tests.agents.test_screens import Recorder
from tests.graph.conftest import create_run, wait_status


def _to_end(client_for: Any) -> str:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = create_run(client)
            wait_status(client, run_id, "waiting_gate1")
            client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
            wait_status(client, run_id, "waiting_gate2")
            res = client.post(f"/api/runs/{run_id}/gates/publish", json={"decision": "approve"})
            assert res.status_code == 200, res.text
            wait_status(client, run_id, "delivered")
            return run_id
    finally:
        set_provider(None)


def _rows(run_id: str) -> list[Artifact]:
    with open_session() as s:
        return list(s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "video")))


def test_full_run_records_a_video_after_gate_2(client_for, env: Path) -> None:
    run_id = _to_end(client_for)
    rows = _rows(run_id)
    paths = sorted(Path(r.path).name for r in rows)
    assert len(rows) == 2 and paths[0].endswith(".chapters.json") and paths[1].endswith(".v1.mp4")
    mp4 = next(r for r in rows if r.path.endswith(".mp4"))
    assert (env / "runs" / mp4.path).is_file() and (env / "runs" / mp4.path).parent.name == "deck"
    with client_for() as client:
        steps = [s["agent"] for s in client.get(f"/api/runs/{run_id}").json()["steps"]]
        assert steps.index("gate2") < steps.index("video") < steps.index("repo")
        assert client.get(f"/api/runs/{run_id}/video/chapters").json() == [{"t": 0.0, "title": "Welcome"}]


def test_failing_recorder_fails_the_step_but_not_the_run(client_for, monkeypatch: pytest.MonkeyPatch) -> None:
    def boom(*_a: Any, **_k: Any) -> None:
        raise video.VideoError("Chromium crashed")

    monkeypatch.setattr(video, "record", boom)
    run_id = _to_end(client_for)  # still reaches repo and the end
    assert _rows(run_id) == []
    with open_session() as s:
        steps = {st.agent: st.status for st in s.scalars(select(AgentStep).where(AgentStep.run_id == run_id))}
    assert steps["video"] == "failed" and steps["repo"] == "done"
    errors = [e for e in load_events(run_id) if e.agent == "video" and e.kind == "error"]
    assert errors and "Chromium crashed" in errors[0].error.message


def test_video_fake_emits_a_placeholder_warning(client_for, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VIDEO_FAKE", "1")
    run_id = _to_end(client_for)
    warnings = [e for e in load_events(run_id) if e.agent == "video" and e.status == "warning"]
    assert len(warnings) == 1
    assert warnings[0].message == "Video is a placeholder clip: VIDEO_FAKE is on"


def test_no_placeholder_warning_without_video_fake(client_for, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("VIDEO_FAKE", raising=False)
    run_id = _to_end(client_for)
    assert not [e for e in load_events(run_id) if e.agent == "video" and e.status == "warning"]


def test_startup_logs_a_warning_when_video_fake_is_set(
    client_for, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv("VIDEO_FAKE", "1")
    with caplog.at_level("WARNING"), client_for():
        pass
    assert any("VIDEO_FAKE" in r.getMessage() for r in caplog.records if r.levelname == "WARNING")
