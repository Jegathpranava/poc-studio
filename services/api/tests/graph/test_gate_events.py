import inspect

from poc_studio.db.models import Event
from poc_studio.db.session import open_session
from poc_studio.routes.events import stream_events
from tests.graph.conftest import create_run, wait_status


def test_gate_decision_event_is_emitted_once(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
        wait_status(client, run_id, "waiting_gate2")
        with open_session() as session:
            msgs = [e.message for e in session.query(Event).filter_by(run_id=run_id, level="gate")]
    assert sum(1 for m in msgs if "approve" in m and "scope" in m) == 1


def test_event_stream_holds_no_request_session() -> None:
    assert "session" not in inspect.signature(stream_events).parameters
