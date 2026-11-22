"""Why a step runs again: the `reason` on the step row and on its "running" event."""

import asyncio

from poc_studio.events import load_events
from poc_studio.graph.revise import rerun_reason
from poc_studio.graph.steps import step_scope
from tests.graph.conftest import create_run, wait_status
from tests.graph.test_step_errors import step_rows


def test_rerun_reason_reads_the_state() -> None:
    assert rerun_reason({"run_id": "r"}, "pitch") is None
    assert rerun_reason({"run_id": "r", "revise_note": {"pitch": "shorter"}}, "pitch") == "revise"
    assert rerun_reason({"run_id": "r", "revise_note": {"pitch": "shorter"}}, "screens") is None
    assert rerun_reason({"run_id": "r", "qa_send_back": "port"}, "port") == "send_back"
    assert rerun_reason({"run_id": "r", "qa_send_back": "port"}, "pitch") is None


async def _runs(run_id: str) -> None:
    async with step_scope(run_id, "pitch"):
        pass
    async with step_scope(
        run_id, "pitch", reason=rerun_reason({"run_id": run_id, "revise_note": {"pitch": ""}}, "pitch")
    ):
        pass
    async with step_scope(run_id, "pitch", reason="send_back"):
        pass
    try:
        async with step_scope(run_id, "pitch"):
            raise RuntimeError("boom")
    except RuntimeError:
        pass
    async with step_scope(run_id, "pitch"):
        pass


def test_reruns_carry_a_reason_on_the_row_and_the_event(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        asyncio.run(_runs(run_id))
    assert [r.reason for r in step_rows(run_id, "pitch")] == [None, "revise", "send_back", "revise", "retry"]
    running = [
        e for e in load_events(run_id) if e.agent == "pitch" and e.kind == "status" and e.status == "running"
    ]
    assert [e.reason for e in running] == [None, "revise", "send_back", "revise", "retry"]
