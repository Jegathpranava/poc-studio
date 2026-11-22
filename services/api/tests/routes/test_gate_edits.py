from tests.graph.conftest import create_run, wait_status

GATE = "/api/runs/{}/gates/{}"
ART = "/api/runs/{}/artifacts/{}"


def test_artifact_404_until_one_exists(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        assert client.get(ART.format(run_id, "architecture")).status_code == 404
        assert client.get(ART.format("r_000000", "requirements")).status_code == 404
        assert client.get(ART.format(run_id, "nonsense")).status_code == 422
        body = client.get(ART.format(run_id, "requirements")).json()
        assert body["type"] == "requirements" and body["version"] == 1
        assert body["data"]["features"]


def test_approve_with_edits_saves_a_new_version(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        brief = client.get(ART.format(run_id, "requirements")).json()["data"]
        brief["budget"] = {"text": "About $99k", "amount_usd": 99000}
        brief["title"] = "Edited by the owner"

        res = client.post(GATE.format(run_id, "scope"), json={"decision": "approve", "edits": brief})
        assert res.status_code == 200 and res.json()["status"] == "running"

        latest = client.get(ART.format(run_id, "requirements")).json()
        assert latest["version"] == 2
        assert latest["data"]["budget"]["amount_usd"] == 99000
        assert latest["data"]["title"] == "Edited by the owner"
        detail = wait_status(client, run_id, "waiting_gate2")
        assert detail["title"] == "Edited by the owner"


def test_invalid_edits_return_422_and_leave_the_gate_open(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        brief = client.get(ART.format(run_id, "requirements")).json()["data"]
        brief["features"] = []
        brief["sector"] = "space-mining"

        res = client.post(GATE.format(run_id, "scope"), json={"decision": "approve", "edits": brief})
        assert res.status_code == 422
        locs = {tuple(e["loc"]) for e in res.json()["detail"]}
        assert ("features",) in locs and ("sector",) in locs

        assert client.get(f"/api/runs/{run_id}").json()["status"] == "waiting_gate1"
        assert client.get(ART.format(run_id, "requirements")).json()["version"] == 1
        assert client.post(GATE.format(run_id, "scope"), json={"decision": "approve"}).status_code == 200


def test_changes_with_a_note_creates_version_2(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        res = client.post(GATE.format(run_id, "scope"), json={"decision": "changes", "note": "Add SMS"})
        assert res.status_code == 200
        wait_status(client, run_id, "waiting_gate1")
        assert client.get(ART.format(run_id, "requirements")).json()["version"] == 2


def _values(client, run_id: str) -> dict:
    graph = client.app.state.run_service.graph
    return client.portal.call(graph.aget_state, {"configurable": {"thread_id": run_id}}).values


def _at_gate1(client) -> tuple[str, dict]:
    run_id = create_run(client)
    wait_status(client, run_id, "waiting_gate1")
    return run_id, client.get(ART.format(run_id, "requirements")).json()["data"]


def test_client_change_returns_422(client_for) -> None:
    with client_for() as client:
        run_id, brief = _at_gate1(client)
        brief["client"] = "Someone Else Ltd"
        res = client.post(GATE.format(run_id, "scope"), json={"decision": "approve", "edits": brief})
        assert res.status_code == 422
        assert ["client"] in [e["loc"] for e in res.json()["detail"]]
        assert client.get(f"/api/runs/{run_id}").json()["status"] == "waiting_gate1"


def test_sector_change_returns_422(client_for) -> None:
    with client_for() as client:
        run_id, brief = _at_gate1(client)
        brief["sector"] = "fintech" if brief["sector"] != "fintech" else "healthcare"
        res = client.post(GATE.format(run_id, "scope"), json={"decision": "approve", "edits": brief})
        assert res.status_code == 422
        assert ["sector"] in [e["loc"] for e in res.json()["detail"]]
        assert client.get(f"/api/runs/{run_id}").json()["status"] == "waiting_gate1"


def test_resumed_state_carries_the_edited_brief(client_for) -> None:
    with client_for() as client:
        run_id, brief = _at_gate1(client)
        brief["title"] = "Edited by the owner"
        brief["summary"] = "A summary the owner rewrote."
        assert (
            client.post(
                GATE.format(run_id, "scope"), json={"decision": "approve", "edits": brief}
            ).status_code
            == 200
        )
        wait_status(client, run_id, "waiting_gate2")
        assert _values(client, run_id)["requirements"] == brief


def test_failed_save_claims_nothing_and_a_retry_succeeds(client_for, monkeypatch) -> None:
    from poc_studio.agents import intelligence
    from poc_studio.db.models import Approval
    from poc_studio.db.session import open_session

    with client_for() as client:
        run_id, brief = _at_gate1(client)
        brief["title"] = "Edited by the owner"
        real = intelligence.write_requirements_file

        def boom(*args, **kwargs):
            raise OSError("disk full")

        monkeypatch.setattr(intelligence, "write_requirements_file", boom)
        res = client.post(GATE.format(run_id, "scope"), json={"decision": "approve", "edits": brief})
        assert res.status_code == 500
        assert "nothing was changed" in res.json()["detail"]
        assert client.get(f"/api/runs/{run_id}").json()["status"] == "waiting_gate1"
        with open_session() as session:
            assert session.query(Approval).filter_by(run_id=run_id).count() == 0
        assert client.get(ART.format(run_id, "requirements")).json()["version"] == 1

        monkeypatch.setattr(intelligence, "write_requirements_file", real)
        res = client.post(GATE.format(run_id, "scope"), json={"decision": "approve", "edits": brief})
        assert res.status_code == 200
        assert client.get(ART.format(run_id, "requirements")).json()["version"] == 2
        wait_status(client, run_id, "waiting_gate2")


def test_version_race_is_retried_once(client_for, monkeypatch) -> None:
    """A concurrent save took version 2 between our read and our insert: the unique path catches it."""
    from poc_studio.agents import intelligence
    from poc_studio.db.session import open_session

    with client_for() as client:
        run_id, brief = _at_gate1(client)
        brief["title"] = "Edited by the owner"
        calls = {"n": 0}
        real = intelligence.next_requirements_version

        def stale(session, rid):
            calls["n"] += 1
            if calls["n"] == 1:
                with open_session() as other:  # the rival writer commits v2 first
                    intelligence.stage_requirements(
                        other, rid, intelligence.Requirements.model_validate(brief)
                    )
                    other.commit()
                return 2  # our stale read
            return real(session, rid)

        monkeypatch.setattr(intelligence, "next_requirements_version", stale)
        res = client.post(GATE.format(run_id, "scope"), json={"decision": "approve", "edits": brief})
        assert res.status_code == 200, res.text
        assert client.get(ART.format(run_id, "requirements")).json()["version"] == 3
