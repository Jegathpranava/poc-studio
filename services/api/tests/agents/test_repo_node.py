import json
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select

from poc_studio.db.models import AgentStep, Artifact
from poc_studio.db.session import open_session
from poc_studio.events import load_events
from poc_studio.llm.client import set_provider
from tests.agents.test_screens import Recorder
from tests.graph.conftest import create_run, wait_status

PLANTED = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4"  # fake token, split so the source holds no secret


def _run(client_for: Any, final: str) -> tuple[str, dict[str, Any]]:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = create_run(client)
            wait_status(client, run_id, "waiting_gate1")
            client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
            wait_status(client, run_id, "waiting_gate2")
            res = client.post(f"/api/runs/{run_id}/gates/publish", json={"decision": "approve"})
            return run_id, {"status": res.status_code, "detail": wait_status(client, run_id, final)}
    finally:
        set_provider(None)


def test_full_mock_run_is_delivered_with_a_repo_artifact(client_for: Any, env: Path) -> None:
    run_id, out = _run(client_for, "delivered")
    assert out["status"] == 200 and out["detail"]["finished_at"] is not None
    with open_session() as s:
        row = s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "repo")).one()
        step = s.scalars(select(AgentStep).where(AgentStep.run_id == run_id, AgentStep.agent == "repo")).one()
    result = json.loads((env / "runs" / row.path).read_text(encoding="utf-8"))
    assert result["repo_url"].startswith("https://github.com/Jegathpranava/") and result["mode"] == "mock"
    assert result["private"] is True and result["pushed"] is False and result["file_count"] > 5
    assert step.status == "done" and step.cost_usd == 0
    assert (env / "runs" / run_id / "publish.mock.json").is_file()
    messages = [e.message or "" for e in load_events(run_id) if e.agent == "repo"]
    assert any("would push (mock mode)" in m for m in messages)


def test_blocked_publish_fails_the_run_with_an_error_event(
    client_for: Any, env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from poc_studio.github import publish as mod

    real = mod.prepare_repo_dir

    def leaky(run_id: str, *, add_ci: bool = True) -> Path:
        out = real(run_id, add_ci=add_ci)
        (out / "app" / "late.ts").write_text(f'export const t = "{PLANTED}";\n', encoding="utf-8")
        return out  # a secret that appears after QA ran: the publish scan must still catch it

    monkeypatch.setattr(mod, "prepare_repo_dir", leaky)
    run_id, out = _run(client_for, "failed")
    assert out["detail"]["status"] == "failed"
    errors = [e for e in load_events(run_id) if e.kind == "error" and e.agent == "repo"]
    assert errors and "Secret scan blocked the push" in (errors[0].error.message if errors[0].error else "")
    assert PLANTED not in json.dumps(
        [(e.message, e.error.message if e.error else "") for e in load_events(run_id)]
    )
    with open_session() as s:
        assert not list(s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "repo")))
    assert not (env / "runs" / run_id / "publish.mock.json").exists()


def test_a_github_error_fails_the_run(client_for: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    from poc_studio.github import publish as mod
    from poc_studio.github.client import GitHubError

    class Down:
        mode = "mock"

        def get_user(self) -> str:
            raise GitHubError("GitHub GET /user failed with HTTP 503")

    monkeypatch.setattr(mod, "get_github", lambda settings: Down())
    run_id, out = _run(client_for, "failed")
    assert out["detail"]["status"] == "failed"
    status = [e for e in load_events(run_id) if e.kind == "error" and e.agent == "repo"]
    assert status and "HTTP 503" in (status[0].error.message if status[0].error else "")
