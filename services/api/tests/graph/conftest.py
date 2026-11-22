"""Graph tests run on real SQLite files (app DB and checkpoints) under pytest's tmp dir."""

import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from poc_studio.config import get_settings
from poc_studio.db import session as db_session
from poc_studio.graph.registry import NodeSpec, collect_nodes
from poc_studio.main import create_app

SAMPLE_VTT = Path(__file__).parents[1] / "ingest" / "fixtures" / "sample.vtt"


def _clear_caches() -> None:
    get_settings.cache_clear()
    db_session.get_engine.cache_clear()
    db_session._factory.cache_clear()


@pytest.fixture
def env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    from poc_studio.db import models  # noqa: F401
    from poc_studio.db.base import Base

    monkeypatch.setenv("POC_DATABASE_URL", f"sqlite:///{(tmp_path / 'app.sqlite').as_posix()}")
    monkeypatch.setenv("RUNS_DIR", str(tmp_path / "runs"))
    _clear_caches()
    Base.metadata.create_all(db_session.get_engine())
    yield tmp_path
    db_session.get_engine().dispose()
    monkeypatch.undo()
    _clear_caches()  # back to the suite's in-memory DB
    Base.metadata.create_all(db_session.get_engine())


@pytest.fixture
def client_for(env: Path):
    """Context manager building a fresh app (a 'process start') on the same DB files."""

    @contextmanager
    def make(nodes: dict[str, NodeSpec] | None = None) -> Iterator[TestClient]:
        with TestClient(create_app(nodes)) as client:
            yield client

    return make


def create_run(client: TestClient, client_name: str = "Acme") -> str:
    res = client.post(
        "/api/runs",
        files=[("files", ("sample.vtt", SAMPLE_VTT.read_bytes(), "text/vtt"))],
        data={"client": client_name, "sector": "logistics"},
    )
    assert res.status_code == 201, res.text
    return res.json()["id"]


def wait_status(client: TestClient, run_id: str, status: str, timeout: float = 15.0) -> dict:
    deadline = time.monotonic() + timeout
    body: dict = {}
    while time.monotonic() < deadline:
        body = client.get(f"/api/runs/{run_id}").json()
        if body["status"] == status:
            return body
        time.sleep(0.05)
    raise AssertionError(f"run stayed {body.get('status')!r}, wanted {status!r}")


def with_node(name: str, fn, owner: str = "test") -> dict[str, NodeSpec]:
    nodes = collect_nodes()
    nodes[name] = NodeSpec(name, fn, owner)
    return nodes


def agents(detail: dict) -> list[str]:
    return [s["agent"] for s in detail["steps"]]
