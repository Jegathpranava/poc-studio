import asyncio
import time
from typing import Any

import pytest

from poc_studio.db.models import Approval, Run
from poc_studio.db.session import open_session
from poc_studio.graph.steps import step_scope
from poc_studio.runs.service import GateError
from tests.graph.conftest import agents, create_run, wait_status, with_node

GATE = "/api/runs/{}/gates/{}"


def test_resume_conflicts_while_a_drive_is_alive(client_for) -> None:
    async def hang(state: dict[str, Any]) -> dict[str, Any]:
        async with step_scope(state["run_id"], "architect"):
            await asyncio.Event().wait()
        return {}

    with client_for(with_node("architect", hang)) as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        client.post(GATE.format(run_id, "scope"), json={"decision": "approve"})
        for _ in range(200):
            if "architect" in agents(client.get(f"/api/runs/{run_id}").json()):
                break
            time.sleep(0.05)
        with pytest.raises(GateError) as err:
            client.portal.call(client.app.state.run_service.resume, run_id)
        assert err.value.code == "conflict"


def test_crash_between_decision_and_drive_is_recovered(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
    # The process died right after decide() committed the Approval and flipped the status.
    with open_session() as session:
        session.add(Approval(run_id=run_id, gate="scope", decision="approve", note="go"))
        run = session.get(Run, run_id)
        assert run is not None
        run.status = "running"
        session.commit()

    with client_for() as client:
        detail = wait_status(client, run_id, "waiting_gate2")
    assert agents(detail).count("intake") == 1 and "architect" in agents(detail)
    with open_session() as session:
        rows = session.query(Approval).filter(Approval.run_id == run_id).all()
        assert len(rows) == 1 and rows[0].consumed_at is not None
