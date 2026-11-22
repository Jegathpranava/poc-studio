import asyncio

from tests.graph.conftest import agents, create_run, wait_status, with_node

GATE = "/api/runs/{}/gates/{}"


def test_full_run_reaches_delivered(client_for, env) -> None:
    with client_for() as client:
        run_id = create_run(client)
        assert run_id.startswith("r_") and len(run_id) == 8
        detail = wait_status(client, run_id, "waiting_gate1")
        assert agents(detail) == ["intake", "intelligence"]
        assert (env / "runs" / run_id / "input" / "sample.vtt").is_file()

        res = client.post(GATE.format(run_id, "scope"), json={"decision": "approve", "edits": {"x": 1}})
        assert res.status_code == 200 and res.json()["status"] == "running"
        detail = wait_status(client, run_id, "waiting_gate2")
        assert agents(detail) == [
            *["intake", "intelligence", "gate1", "architect", "screens"],
            *sorted(["pitch", "port"], key=agents(detail).index),
            *["assemble", "qa"],
        ]
        assert {"pitch", "port"} <= set(agents(detail))

        assert client.post(GATE.format(run_id, "publish"), json={"decision": "approve"}).status_code == 200
        detail = wait_status(client, run_id, "delivered")
        assert agents(detail)[-3:] == ["gate2", "video", "repo"]
        assert detail["finished_at"] is not None
        assert [r["id"] for r in client.get("/api/runs").json()] == [run_id]


def test_gate_conflicts(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        assert client.post(GATE.format(run_id, "publish"), json={"decision": "approve"}).status_code == 409
        assert client.post(GATE.format("r_000000", "scope"), json={"decision": "approve"}).status_code == 404
        assert client.post(GATE.format(run_id, "scope"), json={"decision": "approve"}).status_code == 200
        assert client.post(GATE.format(run_id, "scope"), json={"decision": "approve"}).status_code == 409


def test_restart_at_gate_resumes_from_checkpoint(client_for, env) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
    assert (env / "checkpoints.sqlite").is_file()

    with client_for() as client:  # new app, new graph, same DB files
        assert client.get(f"/api/runs/{run_id}").json()["status"] == "waiting_gate1"
        assert client.post(GATE.format(run_id, "scope"), json={"decision": "approve"}).status_code == 200
        detail = wait_status(client, run_id, "waiting_gate2")
    assert agents(detail).count("intake") == 1  # continued, not restarted
    assert "architect" in agents(detail)


def test_restart_resumes_run_left_running(client_for) -> None:
    async def hang(state):  # the process dies while intelligence is working
        await asyncio.Event().wait()
        return {}

    with client_for(with_node("intelligence", hang)) as client:
        run_id = create_run(client)
        wait_status(client, run_id, "running")
    with client_for() as client:
        detail = wait_status(client, run_id, "waiting_gate1")
    assert agents(detail).count("intake") == 1


def test_gate1_changes_reruns_intelligence(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        body = {"decision": "changes", "note": "budget is 40k, not 4k"}
        assert client.post(GATE.format(run_id, "scope"), json=body).status_code == 200
        detail = wait_status(client, run_id, "waiting_gate1")
        assert agents(detail).count("intelligence") == 2
        assert agents(detail).count("architect") == 0
        assert client.post(GATE.format(run_id, "scope"), json={"decision": "approve"}).status_code == 200
        wait_status(client, run_id, "waiting_gate2")


def test_project_reused_by_case_insensitive_client(client_for) -> None:
    with client_for() as client:
        a, b = create_run(client, "Acme"), create_run(client, "  ACME ")
        rows = {r["id"]: r for r in client.get("/api/runs").json()}
        assert rows[a]["client_name"] == rows[b]["client_name"] == "Acme"


def test_rejects_bad_uploads(client_for) -> None:
    with client_for() as client:
        exe = ("x.exe", b"MZ", "application/octet-stream")
        bad = client.post("/api/runs", files=[("files", exe)], data={"client": "A"})
        assert bad.status_code == 422
        none = client.post("/api/runs", files=[("files", ("a.txt", b"hi", "text/plain"))], data={})
        assert none.status_code == 422
