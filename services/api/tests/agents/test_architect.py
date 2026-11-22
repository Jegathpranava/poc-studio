import json
from typing import Any

import pytest
from pydantic import ValidationError
from sqlalchemy import select

from poc_studio.db.models import AgentStep, Artifact
from poc_studio.db.session import open_session
from poc_studio.llm.provider import FIXTURE_DIR
from poc_studio.schemas.architecture import Architecture
from tests.graph.conftest import create_run, wait_status


def _fixture() -> dict[str, Any]:
    return json.loads((FIXTURE_DIR / "architect.json").read_text(encoding="utf-8"))


def test_mock_output_validates() -> None:
    arch = Architecture.model_validate(_fixture())
    assert 3 <= len(arch.components) <= 12 and arch.mermaid.startswith("flowchart")


def test_total_must_match_lines() -> None:
    data = _fixture()
    data["monthly_cost"]["total_usd"] = 99.0
    with pytest.raises(ValidationError, match="does not match"):
        Architecture.model_validate(data)


def test_mermaid_must_be_a_diagram() -> None:
    data = _fixture()
    data["mermaid"] = "sequenceDiagram\n A->>B: hi"
    with pytest.raises(ValidationError, match="flowchart"):
        Architecture.model_validate(data)


def test_graph_run_writes_architecture(client_for, env) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        res = client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
        assert res.status_code == 200
        wait_status(client, run_id, "waiting_gate2")
        body = client.get(f"/api/runs/{run_id}/artifacts/architecture").json()
        assert body["version"] == 1 and body["data"]["monthly_cost"]["total_usd"] == 45.0
        md = client.get(f"/api/runs/{run_id}/artifacts/architecture/markdown")
        assert md.status_code == 200 and "```mermaid\nflowchart" in md.text
    with open_session() as s:
        arts = list(
            s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "architecture"))
        )
        step = s.scalars(
            select(AgentStep).where(AgentStep.run_id == run_id, AgentStep.agent == "architect")
        ).one()
    assert sorted(a.path.rsplit(".", 1)[1] for a in arts) == ["json", "md"]
    assert {a.version for a in arts} == {1}
    assert step.model == "smart"
    text = (env / "runs" / run_id / "architecture.v1.md").read_text(encoding="utf-8")
    assert "```mermaid\nflowchart" in text and "| **Total** |" in text


def test_markdown_download_rejects_other_types(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        assert client.get(f"/api/runs/{run_id}/artifacts/bogus/markdown").status_code == 422
        assert client.get(f"/api/runs/{run_id}/artifacts/..%2Fapp/markdown").status_code in (404, 422)
        assert client.get(f"/api/runs/{run_id}/artifacts/architecture/markdown").status_code == 404
