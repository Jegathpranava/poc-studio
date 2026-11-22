import json
from pathlib import Path
from typing import Any

from sqlalchemy import select

from poc_studio.db.models import Approval, Artifact
from poc_studio.db.session import open_session
from poc_studio.llm.client import set_provider
from tests.agents.test_screens import Recorder
from tests.graph.conftest import create_run, wait_status

GATE = "/api/runs/{}/gates/publish"


def _to_gate2(client: Any) -> str:
    run_id = create_run(client, "Acme Freight")
    wait_status(client, run_id, "waiting_gate1")
    client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
    wait_status(client, run_id, "waiting_gate2")
    return run_id


def _approvals(run_id: str) -> list[Approval]:
    with open_session() as s:
        return list(s.scalars(select(Approval).where(Approval.run_id == run_id, Approval.gate == "publish")))


def test_block_publish_returns_409_and_leaves_the_gate_open(client_for: Any, env: Path) -> None:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = _to_gate2(client)
            with open_session() as s:
                row = s.scalars(
                    select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "qa_report")
                ).one()
                report = env / "runs" / row.path
            report.write_text(json.dumps(json.loads(report.read_text()) | {"block_publish": True}))
            assert client.get(f"/api/runs/{run_id}/publish").json()["blocked"] is True
            res = client.post(GATE.format(run_id), json={"decision": "approve"})
            assert res.status_code == 409 and "QA blocked the publish" in res.json()["detail"]
            assert client.get(f"/api/runs/{run_id}").json()["status"] == "waiting_gate2"
            assert _approvals(run_id) == []
    finally:
        set_provider(None)


def test_invalid_options_return_422(client_for: Any) -> None:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = _to_gate2(client)
            for bad in (
                {"repo_name": "has space"},
                {"repo_name": "x" * 101},
                {"repo_name": ""},
                {"private": "maybe"},
            ):
                res = client.post(GATE.format(run_id), json={"decision": "approve", "options": bad})
                assert res.status_code == 422, bad
            assert client.get(f"/api/runs/{run_id}").json()["status"] == "waiting_gate2"
    finally:
        set_provider(None)


def test_approve_stores_the_options_and_delivers(client_for: Any) -> None:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = _to_gate2(client)
            pending = client.get(f"/api/runs/{run_id}/publish").json()
            assert pending["status"] == "pending" and pending["result"] is None and pending["mode"] == "mock"
            options = {"repo_name": "acme-dock-poc", "private": True, "open_issues": False, "add_ci": False}
            res = client.post(GATE.format(run_id), json={"decision": "approve", "options": options})
            assert res.status_code == 200
            wait_status(client, run_id, "delivered")
            (row,) = _approvals(run_id)
            assert json.loads(row.edits_json or "{}") == options
            body = client.get(f"/api/runs/{run_id}/publish").json()
            assert body["status"] == "delivered" and body["options"] == options
            assert body["result"]["repo_url"] == "https://github.com/Jegathpranava/acme-dock-poc"
            assert body["result"]["issues"] == [] and body["result"]["private"] is True
    finally:
        set_provider(None)


def test_missing_options_default_to_a_private_repo_named_from_the_client(client_for: Any) -> None:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = _to_gate2(client)
            assert client.post(GATE.format(run_id), json={"decision": "approve"}).status_code == 200
            wait_status(client, run_id, "delivered")
            (row,) = _approvals(run_id)
            saved = json.loads(row.edits_json or "{}")
            assert (
                saved["repo_name"] == "acme-freight-weekly-sales-dashboard-poc" and saved["private"] is True
            )
            assert saved["open_issues"] is True and saved["add_ci"] is True
    finally:
        set_provider(None)


def test_publish_status_is_pending_before_gate_2_and_404_for_unknown(client_for: Any) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        assert client.get(f"/api/runs/{run_id}/publish").json()["status"] == "pending"
        assert client.get("/api/runs/r_000000/publish").status_code == 404
