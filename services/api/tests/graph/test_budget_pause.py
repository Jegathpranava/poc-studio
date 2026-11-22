from typing import Any

from poc_studio.graph.steps import step_scope
from poc_studio.llm import BudgetExceeded
from tests.graph.conftest import agents, create_run, wait_status, with_node


def test_budget_exceeded_pauses_then_resumes(client_for) -> None:
    calls = {"n": 0}

    async def architect(state: dict[str, Any]) -> dict[str, Any]:
        calls["n"] += 1
        async with step_scope(state["run_id"], "architect"):
            if calls["n"] == 1:
                raise BudgetExceeded(needed_usd=0.2, remaining_usd=0.01)
        return {}

    with client_for(with_node("architect", architect)) as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
        detail = wait_status(client, run_id, "paused_budget")
        assert detail["finished_at"] is None
        steps = {s["agent"]: s["status"] for s in detail["steps"]}
        assert steps["architect"] == "paused" and steps["gate1"] == "done"

        events = client.get(f"/api/runs/{run_id}/events?follow=false").text
        assert "paused_budget" in events

        # The checkpoint is kept, so resuming re-runs only the paused node onwards.
        client.portal.call(client.app.state.run_service.resume, run_id)  # type: ignore[union-attr]
        detail = wait_status(client, run_id, "waiting_gate2")
        assert agents(detail).count("intake") == 1 and agents(detail).count("intelligence") == 1
        assert [s["status"] for s in detail["steps"] if s["agent"] == "architect"] == ["paused", "done"]
