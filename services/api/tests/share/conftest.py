"""Share tests: a temp DB and runs dir, the app, and a seeded delivered run."""

import json
import secrets
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient

from poc_studio.agents.store import record
from poc_studio.config import get_settings
from poc_studio.db.models import Project, Run, now
from poc_studio.db.session import open_session
from poc_studio.llm.provider import FIXTURE_DIR
from poc_studio.main import create_app
from poc_studio.share import export
from tests.graph.conftest import client_for, env  # noqa: F401

DECK = "<!doctype html><html><body><h1>Deck</h1><p>Slide one</p></body></html>"


def _fixture(name: str) -> dict[str, Any]:
    data: dict[str, Any] = json.loads((FIXTURE_DIR / f"{name}.json").read_text(encoding="utf-8"))
    return data


@pytest.fixture(autouse=True)
def _fake_pdf(request: pytest.FixtureRequest, monkeypatch: pytest.MonkeyPatch) -> None:
    """Only `browser` tests render a real PDF."""
    if request.node.get_closest_marker("browser"):
        return

    def fake(html: str, out: Path) -> None:
        out.write_bytes(b"%PDF-1.4 fake")

    monkeypatch.setattr(export, "render_pdf", fake)


@pytest.fixture
def client(env: Path) -> Iterator[TestClient]:  # noqa: F811
    with TestClient(create_app()) as c:
        yield c


def seed_run(
    status: str = "delivered",
    *,
    client_name: str = "Acme",
    sector: str | None = "logistics",
    pain_points: list[str] | None = None,
    deck: str | None = DECK,
    video: bool = True,
    started_at: Any = None,
) -> str:
    """A run row with a requirements and architecture artifact, plus a deck and an MP4 on request."""
    req = _fixture("intelligence")
    if pain_points is not None:
        req["pain_points"] = pain_points
    run_id = "r_" + secrets.token_hex(3)
    with open_session() as session:
        project = Project(
            client_name=client_name, client_name_key=f"{client_name}-{run_id}".lower(), sector=sector
        )
        session.add(project)
        session.flush()
        session.add(
            Run(id=run_id, project_id=project.id, title="PoC", status=status, started_at=started_at or now())
        )
        session.commit()
    record(run_id, "requirements", 1, "requirements.v1.json", json.dumps(req).encode())
    record(run_id, "architecture", 1, "architecture.v1.json", json.dumps(_fixture("architect")).encode())
    if deck is not None:
        record(run_id, "deck", 1, "deck/poc.v1.html", deck.encode())
    if video:
        record(run_id, "video", 1, "video/walkthrough.v1.mp4", b"\x00\x00\x00\x18ftypmp42" + b"\x00" * 600)
    return run_id


def run_dir(run_id: str) -> Path:
    return get_settings().runs_dir / run_id
