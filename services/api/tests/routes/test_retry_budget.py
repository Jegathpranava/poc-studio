"""Retry a failed build with a note, resume a failed run, and the budget pause (raise or free model)."""

from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from poc_studio.db.models import Run
from poc_studio.db.session import open_session
from poc_studio.graph.steps import step_scope
from poc_studio.llm import ChatReply
from poc_studio.llm.client import set_provider
from poc_studio.llm.pricing import cost_usd
from poc_studio.sandbox import runner
from poc_studio.sandbox.errors import BuildError
from tests.agents.test_screens import Recorder
from tests.graph.conftest import SAMPLE_VTT, agents, create_run, wait_status, with_node
from tests.routes.test_revise import _counts, _to_gate2

HAIKU = "claude-haiku-5-5"
FIX_NOTE = "The chart import is the problem, do not touch the layout"
ERROR = BuildError(file="app/page.tsx", line=1, col=1, message="Type error", excerpt="> 1 | x")


class PaidRecorder(Recorder):
    """Like the recorder, but a Haiku call reports real token usage, so it costs something."""

    async def chat(self, model: str, messages: list[dict[str, str]], max_tokens: int, timeout: float,
                   agent: str | None = None) -> ChatReply:  # fmt: skip
        reply = await super().chat(model, messages, max_tokens, timeout, agent)
        if agent == "pitch_polish":
            return ChatReply(reply.text, tokens_in=1000, tokens_out=200)
        return reply


def _fail_builds(monkeypatch: pytest.MonkeyPatch, ok_from: int) -> list[int]:
    """Builds number 1..ok_from-1 fail; the rest pass. Returns the attempt numbers seen."""
    seen: list[int] = []

    async def build(app_dir: Path, attempt: int = 1) -> runner.BuildResult:
        seen.append(attempt)
        if len(seen) < ok_from:
            return runner.BuildResult(ok=False, duration_s=0.1, attempt=attempt, log_tail="x", error=ERROR)
        return runner.BuildResult(ok=True, duration_s=0.1, attempt=attempt)

    monkeypatch.setattr(runner, "build", build)
    return seen


def test_retry_with_a_note_reruns_only_port_with_the_note(
    client_for: Any, env: Any, monkeypatch: pytest.MonkeyPatch
) -> None:
    seen = _fail_builds(monkeypatch, ok_from=5)  # 3 builds fail, then the retry: one fail, one pass
    rec = Recorder()
    set_provider(rec)
    try:
        with client_for() as client:
            run_id = _to_gate2(client)
            assert seen == [1, 2, 3]
            first_prompts = len(rec.prompts.get("port", []))
            before = _counts(client.get(f"/api/runs/{run_id}").json())
            res = client.post(f"/api/runs/{run_id}/retry", json={"note": FIX_NOTE})
            assert res.status_code == 200 and res.json()["agent"] == "port"
            detail = wait_status(client, run_id, "waiting_gate2")
    finally:
        set_provider(None)
    after = _counts(detail)
    assert after["port"] == before["port"] + 1
    for agent in ("assemble", "qa"):
        assert after[agent] == before[agent] + 1, agent
    for agent in ("intelligence", "architect", "screens", "pitch"):
        assert after[agent] == before[agent] == 1, agent
    prompts = rec.prompts["port"]
    assert len(prompts) == first_prompts + 1 and FIX_NOTE in prompts[-1]  # one failed build, one fix call
    assert all(FIX_NOTE not in p for p in prompts[:first_prompts])
    assert seen == [1, 2, 3, 1, 2]  # a fresh attempt budget: attempt numbers start again
    assert [s["status"] for s in detail["steps"] if s["agent"] == "port"] == ["failed", "done"]


def test_retry_attempts_limit_the_builds(client_for: Any, env: Any, monkeypatch: pytest.MonkeyPatch) -> None:
    seen = _fail_builds(monkeypatch, ok_from=99)
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = _to_gate2(client)
            assert client.post(f"/api/runs/{run_id}/retry", json={"attempts": 4}).status_code == 422
            client.post(f"/api/runs/{run_id}/retry", json={"attempts": 1})
            wait_status(client, run_id, "waiting_gate2")
            assert seen == [1, 2, 3, 1]  # one more attempt, still failing, back at the gate
    finally:
        set_provider(None)


def test_retry_is_a_conflict_when_nothing_failed(client_for: Any, env: Any) -> None:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = _to_gate2(client)  # the port built fine
            assert client.post(f"/api/runs/{run_id}/retry", json={}).status_code == 409
            assert client.post("/api/runs/nope/retry", json={}).status_code == 404
    finally:
        set_provider(None)


def test_retry_resumes_a_failed_run_from_its_checkpoint(client_for: Any, env: Any) -> None:
    calls = {"n": 0}

    async def architect(state: dict[str, Any]) -> dict[str, Any]:
        calls["n"] += 1
        async with step_scope(state["run_id"], "architect"):
            if calls["n"] == 1:
                raise RuntimeError("gateway down")
        return {}

    with client_for(with_node("architect", architect)) as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
        failed = wait_status(client, run_id, "failed")
        assert failed["finished_at"] is not None
        assert client.post(f"/api/runs/{run_id}/retry", json={}).status_code == 200
        detail = wait_status(client, run_id, "waiting_gate2")
        assert detail["finished_at"] is None
        assert agents(detail).count("intelligence") == 1 and agents(detail).count("architect") == 2


def _paused(client: TestClient) -> str:
    res = client.post(
        "/api/runs",
        files=[("files", ("sample.vtt", SAMPLE_VTT.read_bytes(), "text/vtt"))],
        data={"client": "Acme", "sector": "logistics", "budget_usd": "0.001"},
    )
    run_id = res.json()["id"]
    wait_status(client, run_id, "waiting_gate1")
    client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
    wait_status(client, run_id, "paused_budget")
    return run_id


def _paid(run_id: str) -> float:
    with open_session() as s:
        run = s.get(Run, run_id)
        assert run is not None
        return run.paid_usd


def test_a_raise_resumes_with_no_duplicate_paid_call(client_for: Any, env: Any) -> None:
    rec = PaidRecorder()
    set_provider(rec)
    try:
        with client_for() as client:
            run_id = _paused(client)
            assert "pitch_polish" not in rec.prompts and _paid(run_id) == 0.0
            assert client.post(f"/api/runs/{run_id}/budget", json={"budget_usd": 0.5}).status_code == 200
            detail = wait_status(client, run_id, "waiting_gate2")
    finally:
        set_provider(None)
    assert len(rec.prompts["pitch_polish"]) == 1  # the one Haiku call, made after the raise
    assert detail["budget_usd"] == 0.5
    assert _paid(run_id) == pytest.approx(cost_usd(HAIKU, 1000, 200))  # exactly one call paid for
    counts = _counts(detail)
    assert counts["intelligence"] == 1 and counts["architect"] == 1 and counts["screens"] == 1
    assert [s["status"] for s in detail["steps"] if s["agent"] == "pitch"] == ["paused", "done"]


def test_use_the_free_model_finishes_the_pitch_without_haiku(client_for: Any, env: Any) -> None:
    rec = PaidRecorder()
    set_provider(rec)
    try:
        with client_for() as client:
            run_id = _paused(client)
            res = client.post(f"/api/runs/{run_id}/budget", json={"use_free_model": True})
            assert res.status_code == 200
            wait_status(client, run_id, "waiting_gate2")
            # the choice sticks: a deck revision does not polish either
            client.post(f"/api/runs/{run_id}/artifacts/deck/revise", json={"note": "Shorter"})
            wait_status(client, run_id, "waiting_gate2")
    finally:
        set_provider(None)
    assert "pitch_polish" not in rec.prompts
    assert _paid(run_id) == 0.0


def test_invalid_budgets_are_rejected(client_for: Any, env: Any) -> None:
    set_provider(PaidRecorder())
    try:
        with client_for() as client:
            run_id = _paused(client)
            url = f"/api/runs/{run_id}/budget"
            assert client.post(url, json={}).status_code == 422
            for bad in (0, -1, 1.5, 100):
                assert client.post(url, json={"budget_usd": bad}).status_code == 422, bad
            with open_session() as s:
                run = s.get(Run, run_id)
                assert run is not None
                run.paid_usd = 0.3
                s.commit()
            assert client.post(url, json={"budget_usd": 0.3}).status_code == 422  # not above what was spent
            assert client.post(url, json={"budget_usd": 0.2}).status_code == 422
            assert client.get(f"/api/runs/{run_id}").json()["status"] == "paused_budget"
            assert client.post(url, json={"budget_usd": 0.31}).status_code == 200
            wait_status(client, run_id, "waiting_gate2")
            assert client.post(url, json={"budget_usd": 0.5}).status_code == 409  # no longer paused
            assert client.post("/api/runs/nope/budget", json={"budget_usd": 0.5}).status_code == 404
    finally:
        set_provider(None)
