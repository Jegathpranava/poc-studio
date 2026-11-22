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
