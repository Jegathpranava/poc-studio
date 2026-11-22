import time
from typing import Any

import pytest

from poc_studio.db.models import Run
from poc_studio.db.session import open_session
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.spend import node_budget
from poc_studio.graph.steps import step_scope
from poc_studio.llm import BudgetExceeded
from tests.graph.conftest import SAMPLE_VTT, create_run, wait_status, with_node

GATE = "/api/runs/{}/gates/{}"


def spender(name: str):
    async def fn(state: dict[str, Any]) -> dict[str, Any]:
        async with step_scope(state["run_id"], name):
            budget = node_budget(state)
            budget.charge(0.01)
            return {"spent_delta": budget.charged_usd}

    return fn


def values(client, run_id: str) -> dict[str, Any]:
    graph = client.app.state.run_service.graph
    snap = client.portal.call(graph.aget_state, {"configurable": {"thread_id": run_id}})
    return snap.values


def test_parallel_branches_both_count(client_for) -> None:
    nodes = with_node("pitch", spender("pitch"))
    nodes["port"] = NodeSpec("port", spender("port"), "test")
    with client_for(nodes) as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        client.post(GATE.format(run_id, "scope"), json={"decision": "approve"})
        detail = wait_status(client, run_id, "waiting_gate2")
        assert detail["paid_usd"] == pytest.approx(0.02)
        state = values(client, run_id)
        assert state["spent_delta"] == pytest.approx(0.02)
        assert state["limit_usd"] > 0


def test_charges_of_a_failed_attempt_stay_in_paid_usd(client_for) -> None:
    async def architect(state: dict[str, Any]) -> dict[str, Any]:
        async with step_scope(state["run_id"], "architect"):
            node_budget(state).charge(0.01)
            raise BudgetExceeded(0.5, 0.0)

    with client_for(with_node("architect", architect)) as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        client.post(GATE.format(run_id, "scope"), json={"decision": "approve"})
        detail = wait_status(client, run_id, "paused_budget")
        assert detail["paid_usd"] == pytest.approx(0.01)


def run_with_budget(client, budget: float) -> str:
    res = client.post(
        "/api/runs",
        files=[("files", ("sample.vtt", SAMPLE_VTT.read_bytes(), "text/vtt"))],
        data={"client": "Acme", "budget_usd": str(budget)},
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def wait_steps(client, run_id: str, agent: str, expected: list[str], timeout: float = 15.0) -> None:
    deadline = time.monotonic() + timeout
    got: list[str] = []
    while time.monotonic() < deadline:
        detail = client.get(f"/api/runs/{run_id}").json()
        got = [s["status"] for s in detail["steps"] if s["agent"] == agent]
        if got == expected and detail["status"] != "running":
            return
        time.sleep(0.05)
    raise AssertionError(f"{agent} steps were {got}, wanted {expected}")


def test_resume_with_a_higher_budget_progresses(client_for) -> None:
    async def architect(state: dict[str, Any]) -> dict[str, Any]:
        async with step_scope(state["run_id"], "architect"):
            node_budget(state).check("claude-haiku-5-5", "word " * 200, 100)  # needs about $0.00007
        return {}

    with client_for(with_node("architect", architect)) as client:
        service = client.app.state.run_service
        run_id = run_with_budget(client, 1e-5)
        wait_status(client, run_id, "waiting_gate1")
        client.post(GATE.format(run_id, "scope"), json={"decision": "approve"})
        wait_steps(client, run_id, "architect", ["paused"])

        client.portal.call(service.resume, run_id)  # same limit: pauses again
        wait_steps(client, run_id, "architect", ["paused", "paused"])
        assert client.get(f"/api/runs/{run_id}").json()["status"] == "paused_budget"

        client.portal.call(service.resume, run_id, 1.0)
        detail = wait_status(client, run_id, "waiting_gate2")
        assert detail["budget_usd"] == 1.0
        assert values(client, run_id)["limit_usd"] == 1.0
        with open_session() as session:
            run = session.get(Run, run_id)
            assert run is not None and run.budget_usd == 1.0
