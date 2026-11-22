import asyncio
import logging
import time
from typing import Any

from poc_studio.db.models import AgentStep
from poc_studio.db.session import open_session
from poc_studio.graph.steps import step_scope
from tests.graph.conftest import create_run, wait_status, with_node

GATE = "/api/runs/{}/gates/{}"
TOKEN = "gh" + "p_" + "a1B2c3D4e5" * 3 + "xyz123"


def step_rows(run_id: str, agent: str) -> list[AgentStep]:
    with open_session() as session:
        return list(session.query(AgentStep).filter_by(run_id=run_id, agent=agent).order_by(AgentStep.id))


def test_failed_step_error_is_stored_and_logged_redacted(client_for, caplog) -> None:
    async def architect(state: dict[str, Any]) -> dict[str, Any]:
        async with step_scope(state["run_id"], "architect"):
            raise RuntimeError(f"auth failed with {TOKEN} " + "x" * 600)

    caplog.set_level(logging.INFO)
    with client_for(with_node("architect", architect)) as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        client.post(GATE.format(run_id, "scope"), json={"decision": "approve"})
        wait_status(client, run_id, "failed")
    (row,) = step_rows(run_id, "architect")
    assert row.error_message is not None
    assert TOKEN not in row.error_message and "[REDACTED]" in row.error_message
    assert len(row.error_message) <= 500
    assert TOKEN not in caplog.text


def test_cancelled_step_is_marked_interrupted(client_for) -> None:
    async def hang(state: dict[str, Any]) -> dict[str, Any]:
        async with step_scope(state["run_id"], "intelligence"):
            await asyncio.Event().wait()
        return {}

    with client_for(with_node("intelligence", hang)) as client:
        run_id = create_run(client)
        wait_status(client, run_id, "running")
        for _ in range(200):
            if step_rows(run_id, "intelligence"):
                break
            time.sleep(0.05)
    assert [r.status for r in step_rows(run_id, "intelligence")] == ["interrupted"]
    with client_for() as client:
        wait_status(client, run_id, "waiting_gate1")
    assert [r.status for r in step_rows(run_id, "intelligence")] == ["interrupted", "done"]
    assert [r.reason for r in step_rows(run_id, "intelligence")] == [None, "retry"]
