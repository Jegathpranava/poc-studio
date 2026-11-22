import httpx
import pytest
from pydantic import SecretStr

from poc_studio.config import get_settings
from poc_studio.routes import settings as settings_routes


def _fake(prefix: str) -> str:
    return prefix + "Zq7" * 10  # built at run time, never a literal


GATEWAY_VALUE = _fake("sk-")
GITHUB_VALUE = _fake("ghp_")


@pytest.fixture
def secrets_set(client, monkeypatch: pytest.MonkeyPatch) -> None:
    s = get_settings()
    monkeypatch.setattr(s, "openai_api_key", SecretStr(GATEWAY_VALUE))
    monkeypatch.setattr(s, "github_token", SecretStr(GITHUB_VALUE))


def test_get_never_contains_key_values(client, secrets_set) -> None:
    res = client.get("/api/settings")
    assert res.status_code == 200
    assert GATEWAY_VALUE not in res.text and GITHUB_VALUE not in res.text
    body = res.json()
    assert body["gateway"]["api_key_set"] is True and body["github"]["token_set"] is True
    assert body["github"]["private_default"] is True
    assert set(body["gateway"]) == {"base_url", "fast_model", "smart_model", "polish_model", "api_key_set"}
    assert set(body["budget"]) == {"run_limit_usd", "monthly_cap_usd", "hours_saved_per_run"}


def test_key_not_set_reads_false(client, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "openai_api_key", SecretStr(""))
    assert client.get("/api/settings").json()["gateway"]["api_key_set"] is False


def test_put_updates_the_budget_and_persists(client, env, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(get_settings(), "run_budget_usd", 0.05)
    res = client.put("/api/settings", json={"budget": {"run_limit_usd": 0.08, "hours_saved_per_run": 6}})
    assert res.status_code == 200
    assert res.json()["budget"]["run_limit_usd"] == 0.08
    assert res.json()["budget"]["hours_saved_per_run"] == 6
    assert get_settings().run_budget_usd == 0.08
    assert (env / "settings.json").is_file()
    client.put("/api/settings", json={"retention_days": 7})
    again = client.get("/api/settings").json()
    assert again["budget"]["run_limit_usd"] == 0.08 and again["retention_days"] == 7  # merged, not replaced


def test_put_refuses_secrets_and_bad_values(client, env) -> None:
    assert client.put("/api/settings", json={"gateway": {"api_key": "x"}}).status_code == 422
    assert client.put("/api/settings", json={"openai_api_key": "x"}).status_code == 422
    assert client.put("/api/settings", json={"budget": {"run_limit_usd": -1}}).status_code == 422
    assert client.put("/api/settings", json={"gateway": {"base_url": "ftp://x"}}).status_code == 422


def test_put_never_writes_env(client, env) -> None:
    from poc_studio.qa.secrets import env_file_path

    path = env_file_path()
    before = path.read_bytes() if path and path.is_file() else None
    client.put("/api/settings", json={"gateway": {"fast_model": "fast"}})
    after = path.read_bytes() if path and path.is_file() else None
    assert before == after
    assert not (env / ".env").exists()


def test_test_gateway_in_mock_mode_makes_no_network_call(client, monkeypatch: pytest.MonkeyPatch) -> None:
    def no_network() -> httpx.Client:
        raise AssertionError("network used")

    monkeypatch.setattr(settings_routes, "_client", no_network)
    res = client.post("/api/settings/test-gateway")
    assert res.status_code == 200 and res.json()["ok"] is True and res.json()["models"]


def _gateway_mode(monkeypatch: pytest.MonkeyPatch, handler) -> None:  # noqa: ANN001
    s = get_settings()
    monkeypatch.setattr(s, "llm_provider", "gateway")
    monkeypatch.setattr(s, "openai_api_key", SecretStr(GATEWAY_VALUE))
    transport = httpx.MockTransport(handler)
    monkeypatch.setattr(settings_routes, "_client", lambda: httpx.Client(transport=transport))


def test_test_gateway_lists_models_only(client, monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[httpx.Request] = []

    def handler(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return httpx.Response(200, json={"data": [{"id": "fast"}, {"id": "smart"}]})

    _gateway_mode(monkeypatch, handler)
    res = client.post("/api/settings/test-gateway")
    assert res.json() == {"ok": True, "models": ["fast", "smart"], "error": None}
    assert [(r.method, r.url.path) for r in seen] == [("GET", "/v1/models")]
    assert GATEWAY_VALUE not in res.text


def test_test_gateway_failure_is_reported_without_the_key(client, monkeypatch: pytest.MonkeyPatch) -> None:
    _gateway_mode(monkeypatch, lambda request: httpx.Response(401, text=f"bad key {GATEWAY_VALUE}"))
    body = client.post("/api/settings/test-gateway").json()
    assert body["ok"] is False and GATEWAY_VALUE not in str(body)
