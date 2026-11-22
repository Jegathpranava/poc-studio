import pytest
from fastapi.testclient import TestClient

APP = "http://127.0.0.1:3000"
FOREIGN = "http://127.0.0.1:4300"


def test_text_plain_post_from_a_foreign_origin_is_403(client: TestClient) -> None:
    res = client.post(
        "/api/settings/test-gateway", content="{}", headers={"Origin": FOREIGN, "Content-Type": "text/plain"}
    )
    assert res.status_code == 403


def test_json_post_from_a_foreign_origin_is_403(client: TestClient) -> None:
    res = client.post("/api/settings/test-gateway", json={}, headers={"Origin": FOREIGN})
    assert res.status_code == 403


@pytest.mark.parametrize("origin", [APP, "http://localhost:3000"])
def test_json_post_from_the_app_origin_passes(client: TestClient, origin: str) -> None:
    res = client.post("/api/settings/test-gateway", json={}, headers={"Origin": origin})
    assert res.status_code == 200


def test_text_plain_from_the_app_origin_is_403(client: TestClient) -> None:
    res = client.post(
        "/api/settings/test-gateway", content="{}", headers={"Origin": APP, "Content-Type": "text/plain"}
    )
    assert res.status_code == 403


def test_a_post_without_origin_passes(client: TestClient) -> None:
    assert client.post("/api/settings/test-gateway").status_code == 200


def test_multipart_run_creation_from_the_app_origin_passes(client: TestClient) -> None:
    res = client.post(
        "/api/runs",
        files=[("files", ("call.txt", b"We ship pallets. Budget is 20k.", "text/plain"))],
        data={"client": "Acme", "sector": "logistics"},
        headers={"Origin": APP},
    )
    assert res.status_code == 201, res.text


def test_put_and_delete_are_guarded_too(client: TestClient) -> None:
    assert client.put("/api/settings", content="{}", headers={"Origin": FOREIGN}).status_code == 403
    assert client.delete("/api/runs/x", headers={"Origin": FOREIGN}).status_code == 403


def test_gets_are_never_blocked(client: TestClient) -> None:
    assert client.get("/api/health", headers={"Origin": FOREIGN}).status_code == 200


def test_a_bad_host_is_400(client: TestClient) -> None:
    assert client.get("/api/health", headers={"Host": "evil.example"}).status_code == 400


@pytest.mark.parametrize("host", ["127.0.0.1:8000", "localhost:8000", "testserver"])
def test_local_hosts_are_allowed(client: TestClient, host: str) -> None:
    assert client.get("/api/health", headers={"Host": host}).status_code == 200
