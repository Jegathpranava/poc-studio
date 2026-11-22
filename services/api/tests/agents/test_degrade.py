"""Pitch and assemble degrade like port: a failed step with an error event; the run still reaches Gate 2."""

import json
from typing import Any

import pytest
from sqlalchemy import select

from poc_studio.db.models import AgentStep
from poc_studio.db.session import open_session
from poc_studio.events import load_events
from poc_studio.graph.registry import collect_nodes
from poc_studio.llm.client import set_provider
from poc_studio.llm.provider import FIXTURE_DIR, ChatReply
from tests.agents.test_screens import Recorder
from tests.graph.conftest import create_run, wait_status


async def _empty(state: Any) -> dict[str, Any]:
    return {}


class AlwaysInvalidPitch(Recorder):
    """The mock provider, except that every pitch reply is the invalid first plan."""

    async def chat(self, model, messages, max_tokens, timeout, agent=None) -> ChatReply:  # type: ignore[no-untyped-def]
        if agent == "pitch":
            self.prompts.setdefault("pitch", []).append("\n".join(m["content"] for m in messages))
            plans = json.loads((FIXTURE_DIR / "pitch.json").read_text(encoding="utf-8"))
            return ChatReply(text=json.dumps(plans[0]), tokens_in=0, tokens_out=0)
        return await super().chat(model, messages, max_tokens, timeout, agent)


def _step(run_id: str, agent: str) -> AgentStep:
    with open_session() as s:
        step = s.scalars(select(AgentStep).where(AgentStep.run_id == run_id, AgentStep.agent == agent)).one()
        s.expunge(step)
        return step


def _errors(run_id: str, agent: str) -> list[Any]:
    return [e for e in load_events(run_id) if e.agent == agent and e.kind == "error"]


def _drive(client_for: Any, rec: Recorder, nodes: Any = None) -> str:
    set_provider(rec)
    try:
        with client_for(nodes) as client:
            run_id = create_run(client)
            wait_status(client, run_id, "waiting_gate1")
            client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
            wait_status(client, run_id, "waiting_gate2")
            return run_id
    finally:
        set_provider(None)


def test_real_run_with_missing_inputs_fails_the_steps_but_reaches_gate2(
    client_for, env, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("POC_ALLOW_STUB_SKIP")  # a real run, not a stub-node graph
    nodes = collect_nodes()
    from poc_studio.graph.registry import NodeSpec

    nodes["screens"] = NodeSpec("screens", _empty, "test")  # no screenpack is ever produced
    nodes["port"] = NodeSpec("port", _empty, "test")
    run_id = _drive(client_for, Recorder(), nodes)
    for agent in ("pitch", "assemble"):
        step = _step(run_id, agent)
        assert step.status == "failed" and step.error_message
        assert _errors(run_id, agent), agent


def test_stub_graphs_still_skip_silently(client_for, env) -> None:
    from poc_studio.graph.registry import NodeSpec

    nodes = collect_nodes()
    nodes["screens"] = NodeSpec("screens", _empty, "test")
    nodes["port"] = NodeSpec("port", _empty, "test")
    run_id = _drive(client_for, Recorder(), nodes)  # POC_ALLOW_STUB_SKIP=1 from the env fixture
    assert _step(run_id, "pitch").status == "done" and _step(run_id, "assemble").status == "done"
    assert not _errors(run_id, "pitch")


def test_pitch_with_invalid_plans_after_repairs_fails_and_the_run_reaches_gate2(
    client_for, env, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.delenv("POC_ALLOW_STUB_SKIP")
    rec = AlwaysInvalidPitch()
    run_id = _drive(client_for, rec)
    assert len(rec.prompts["pitch"]) == 3  # first try plus two repairs
    step = _step(run_id, "pitch")
    assert step.status == "failed" and "Deck plan invalid" in (step.error_message or "")
    assert _errors(run_id, "pitch")
    assert "pitch_polish" not in rec.prompts
    # assemble has no deck plan to work with: a failed step too, and the run still got here
    assert _step(run_id, "assemble").status == "failed" and _errors(run_id, "assemble")
