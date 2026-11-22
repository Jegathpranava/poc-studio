import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from poc_studio.config import Settings
from poc_studio.main import app


def test_health_ok_with_mock_provider() -> None:
    with TestClient(app) as client:
        body = client.get("/api/health").json()
    assert body == {"status": "ok", "llm_provider": "mock", "github_mode": "mock", "db": "ok"}


def test_runs_list_empty() -> None:
    with TestClient(app) as client:
        res = client.get("/api/runs")
    assert res.status_code == 200
    assert res.json() == []


def test_production_refuses_mock_llm() -> None:
    with pytest.raises(ValidationError):
        Settings(APP_ENV="production", LLM_PROVIDER="mock", GITHUB_MODE="live")  # type: ignore[arg-type]


def test_production_refuses_mock_github() -> None:
    with pytest.raises(ValidationError):
        Settings(APP_ENV="production", LLM_PROVIDER="gateway", GITHUB_MODE="mock")  # type: ignore[arg-type]
