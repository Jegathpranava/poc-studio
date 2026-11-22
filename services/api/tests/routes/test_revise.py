"""Request changes at Gate 2: only the owning agent and what follows it rerun (asserted on step rows)."""

from collections import Counter
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import select

from poc_studio.db.models import AgentStep, Artifact
from poc_studio.db.session import open_session
from poc_studio.llm.client import set_provider
from poc_studio.schemas.deck import DeckPlan
from tests.agents.test_screens import Recorder
from tests.graph.conftest import agents, create_run, wait_status

NOTE = "Lead with the cost saving and keep it to nine slides"


def _to_gate2(client: TestClient) -> str:
    run_id = create_run(client)
    wait_status(client, run_id, "waiting_gate1")
    client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
    wait_status(client, run_id, "waiting_gate2")
    return run_id


def _revise(client: TestClient, run_id: str, kind: str, note: str = NOTE) -> dict[str, Any]:
    res = client.post(f"/api/runs/{run_id}/artifacts/{kind}/revise", json={"note": note})
    assert res.status_code == 200, res.text
    return wait_status(client, run_id, "waiting_gate2")


def _counts(detail: dict[str, Any]) -> Counter[str]:
    return Counter(agents(detail))


def test_revising_the_deck_reruns_pitch_assemble_and_qa_only(client_for: Any, env: Any) -> None:
    rec = Recorder()
    set_provider(rec)
    try:
        with client_for() as client:
            run_id = _to_gate2(client)
            before = _counts(client.get(f"/api/runs/{run_id}").json())
            detail = _revise(client, run_id, "deck")
    finally:
        set_provider(None)
    after = _counts(detail)
    for agent in ("pitch", "assemble", "qa"):
        assert after[agent] == before[agent] + 1, agent
    for agent in ("intelligence", "architect", "screens", "port", "intake"):
        assert after[agent] == before[agent] == 1, agent
    assert after["gate2"] == 1  # a gate row is written when its decision is taken
    assert NOTE in rec.prompts["pitch"][-1]
    assert all(NOTE not in p for p in rec.prompts["pitch"][:-1])
    with open_session() as s:
        deck = s.scalars(
            select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "deck").order_by(Artifact.id)
        ).all()
        steps = s.scalars(
            select(AgentStep)
            .where(AgentStep.run_id == run_id, AgentStep.agent == "pitch")
            .order_by(AgentStep.id)
        ).all()
    # the plan and the assembled html each count v1, v2 on their own
    assert sorted(a.version for a in deck if a.path.endswith(".json")) == [1, 2]
    assert sorted(a.version for a in deck if a.path.endswith(".html")) == [1, 2]
    assert [(s.attempt, s.reason) for s in steps] == [(1, None), (2, "revise")]
    plan_file = env / "runs" / run_id / "deck" / "plan.v2.json"
    plan = DeckPlan.model_validate_json(plan_file.read_text(encoding="utf-8"))
    assert plan.slides


def test_the_note_is_used_once(client_for: Any, env: Any) -> None:
    rec = Recorder()
    set_provider(rec)
    try:
        with client_for() as client:
            run_id = _to_gate2(client)
            _revise(client, run_id, "deck")
            detail = _revise(client, run_id, "deck", "Shorter closing slide")
    finally:
        set_provider(None)
    assert _counts(detail)["pitch"] == 3
    assert "Shorter closing slide" in rec.prompts["pitch"][-1] and NOTE not in rec.prompts["pitch"][-1]


def test_revising_the_prototype_reruns_screens_port_and_pitch(client_for: Any, env: Any) -> None:
    rec = Recorder()
    set_provider(rec)
    try:
        with client_for() as client:
            run_id = _to_gate2(client)
            before = _counts(client.get(f"/api/runs/{run_id}").json())
            detail = _revise(client, run_id, "prototype")
    finally:
        set_provider(None)
    after = _counts(detail)
    for agent in ("screens", "port", "pitch", "assemble", "qa"):
        assert after[agent] == before[agent] + 1, agent
    for agent in ("intelligence", "architect"):
        assert after[agent] == before[agent] == 1, agent
    assert NOTE in rec.prompts["screens"][-1]
    assert all(NOTE not in p for p in rec.prompts["pitch"])


def test_revising_the_architecture_reruns_everything_after_it(client_for: Any, env: Any) -> None:
    rec = Recorder()
    set_provider(rec)
    try:
        with client_for() as client:
            run_id = _to_gate2(client)
            before = _counts(client.get(f"/api/runs/{run_id}").json())
            detail = _revise(client, run_id, "architecture")
    finally:
        set_provider(None)
    after = _counts(detail)
    for agent in ("architect", "screens", "port", "pitch", "assemble", "qa"):
        assert after[agent] == before[agent] + 1, agent
    assert after["intelligence"] == before["intelligence"] == 1
    assert NOTE in rec.prompts["architect"][-1]


def test_changes_without_revise_still_waits_at_the_gate(client_for: Any, env: Any) -> None:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = _to_gate2(client)
            res = client.post(f"/api/runs/{run_id}/gates/publish", json={"decision": "changes"})
            assert res.status_code == 200
            detail = wait_status(client, run_id, "waiting_gate2")
            assert _counts(detail)["pitch"] == 1 and _counts(detail)["gate2"] == 1
    finally:
        set_provider(None)


def test_brief_revision_at_gate1_goes_back_to_intelligence(client_for: Any, env: Any) -> None:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = create_run(client)
            wait_status(client, run_id, "waiting_gate1")
            res = client.post(f"/api/runs/{run_id}/artifacts/brief/revise", json={"note": "Add a budget"})
            assert res.status_code == 200 and res.json()["agent"] == "intelligence"
            detail = wait_status(client, run_id, "waiting_gate1")
            assert _counts(detail)["intelligence"] == 2
    finally:
        set_provider(None)


def test_conflicts_and_bad_input(client_for: Any, env: Any) -> None:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = create_run(client)
            wait_status(client, run_id, "waiting_gate1")
            url = f"/api/runs/{run_id}/artifacts/deck/revise"
            assert client.post(url, json={"note": NOTE}).status_code == 409  # still at Gate 1
            client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
            wait_status(client, run_id, "waiting_gate2")
            brief = f"/api/runs/{run_id}/artifacts/brief/revise"
            assert client.post(brief, json={"note": NOTE}).status_code == 409  # not at Gate 1 any more
            assert client.post(url, json={"note": "  "}).status_code == 422
            assert client.post(url, json={}).status_code == 422
            video = f"/api/runs/{run_id}/artifacts/video/revise"
            assert client.post(video, json={"note": NOTE}).status_code == 422
            assert client.post("/api/runs/nope/artifacts/deck/revise", json={"note": NOTE}).status_code == 404
            assert client.post(url, json={"note": NOTE}).status_code == 200
            assert client.post(url, json={"note": NOTE}).status_code in (200, 409)
            wait_status(client, run_id, "waiting_gate2")
    finally:
        set_provider(None)
