import json
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select

from poc_studio.db.models import AgentStep, Artifact
from poc_studio.db.session import open_session
from poc_studio.events import load_events
from poc_studio.llm.client import set_provider
from poc_studio.sandbox import runner
from tests.agents.test_screens import Recorder
from tests.graph.conftest import create_run, wait_status, with_node

PLANTED = "ghp_" + "a1B2c3D4e5F6g7H8i9J0k1L2m3N4"  # fake token, split so the source holds no secret


def _drive(client_for: Any, nodes: Any = None) -> str:
    set_provider(Recorder())
    try:
        with client_for(nodes) as client:
            run_id = create_run(client)
            wait_status(client, run_id, "waiting_gate1")
            client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
            wait_status(client, run_id, "waiting_gate2")
            return run_id
    finally:
        set_provider(None)


def _reports(env: Path, run_id: str) -> list[dict[str, Any]]:
    with open_session() as s:
        rows = s.scalars(
            select(Artifact)
            .where(Artifact.run_id == run_id, Artifact.type == "qa_report")
            .order_by(Artifact.version)
        ).all()
        paths = [r.path for r in rows]
    return [json.loads((env / "runs" / p).read_text(encoding="utf-8")) for p in paths]


def _steps(run_id: str, agent: str) -> int:
    with open_session() as s:
        query = select(AgentStep).where(AgentStep.run_id == run_id, AgentStep.agent == agent)
        return len(list(s.scalars(query)))


def test_mock_run_reaches_gate2_with_a_passing_qa_report(client_for, env: Path) -> None:
    run_id = _drive(client_for)
    (report,) = _reports(env, run_id)
    assert report["failed"] == [], report["checks"]
    assert report["send_back"] is None and report["block_publish"] is False and report["sent_back_count"] == 0
    assert {c["name"] for c in report["checks"]} >= {"deck_present", "no_secrets", "spotlights_resolve"}
    assert (env / "runs" / run_id / "qa_report.v1.json").is_file()
    assert _steps(run_id, "qa") == 1


def test_planted_secret_sends_port_back_twice_then_blocks_publish(
    client_for, env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_install = runner.install

    async def leaky_install(app_dir: Path) -> Any:
        (app_dir / "app").mkdir(parents=True, exist_ok=True)
        (app_dir / "app" / "leak.ts").write_text(f'export const t = "{PLANTED}";\n', encoding="utf-8")
        return await real_install(app_dir)

    monkeypatch.setattr(runner, "install", leaky_install)
    run_id = _drive(client_for)
    reports = _reports(env, run_id)
    assert [r["send_back"] for r in reports] == ["port", "port", None]
    assert [r["sent_back_count"] for r in reports] == [0, 1, 2]
    assert all(r["block_publish"] for r in reports)
    assert "no_secrets" in reports[-1]["failed"]
    assert _steps(run_id, "port") == 3 and _steps(run_id, "qa") == 3
    assert PLANTED not in json.dumps(reports)
    assert PLANTED not in " ".join((e.message or "") for e in load_events(run_id))
    texts = [e.message or "" for e in load_events(run_id) if e.agent == "qa"]
    messages = [t for t in texts if "no_secrets" in t]
    assert messages and "app/leak.ts:1 github_token" in messages[0]


def test_missing_deck_fails_deck_present_and_the_run_still_reaches_gate2(client_for, env: Path) -> None:
    async def failing_assemble(state: Any) -> dict[str, Any]:
        return {"deck_result": {"ok": False, "error": "assemble failed"}}

    run_id = _drive(client_for, with_node("assemble", failing_assemble))
    (report,) = _reports(env, run_id)
    assert "deck_present" in report["failed"]
    assert report["send_back"] is None  # report-only: the run goes on to Gate 2
    present = next(c for c in report["checks"] if c["name"] == "deck_present")
    assert present["owner_agent"] == "assemble" and not present["ok"]
    assert any(e.agent == "qa" and "deck_present" in (e.message or "") for e in load_events(run_id))


def test_real_run_without_a_deck_is_flagged_even_without_a_failure_marker(
    client_for, env: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("POC_ALLOW_STUB_SKIP")

    async def silent_assemble(state: Any) -> dict[str, Any]:
        return {}

    run_id = _drive(client_for, with_node("assemble", silent_assemble))
    (report,) = _reports(env, run_id)
    assert "deck_present" in report["failed"]
