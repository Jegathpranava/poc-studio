from typing import Any

from sqlalchemy import select

from poc_studio.db.models import AgentStep, Artifact, Project, Run
from poc_studio.db.session import open_session
from poc_studio.events import load_events
from poc_studio.llm import ChatReply
from poc_studio.llm.client import set_provider
from poc_studio.llm.provider import MockProvider
from poc_studio.schemas.requirements import Requirements
from tests.graph.conftest import create_run, wait_status

GATE = "/api/runs/{}/gates/{}"


class Recorder:
    """Wraps the mock provider and keeps every prompt it was sent."""

    def __init__(self) -> None:
        self.inner = MockProvider()
        self.prompts: list[str] = []

    async def chat(self, model: str, messages: list[dict[str, str]], max_tokens: int, timeout: float,
                   agent: str | None = None) -> ChatReply:  # fmt: skip
        self.prompts.append("\n".join(m["content"] for m in messages))
        return await self.inner.chat(model, messages, max_tokens, timeout, agent)


def _artifacts(run_id: str) -> list[Artifact]:
    with open_session() as s:
        return list(
            s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "requirements"))
        )


def _brief(env: Any, run_id: str, version: int = 1) -> Requirements:
    path = env / "runs" / run_id / f"requirements.v{version}.json"
    return Requirements.model_validate_json(path.read_text(encoding="utf-8"))


def test_mock_output_validates() -> None:
    import json

    from poc_studio.llm.provider import FIXTURE_DIR

    data = json.loads((FIXTURE_DIR / "intelligence.json").read_text(encoding="utf-8"))
    assert len(Requirements.model_validate(data).features) == 3


def test_node_writes_artifact_and_step(client_for, env) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
    arts = _artifacts(run_id)
    assert [(a.version, len(a.sha256 or "")) for a in arts] == [(1, 64)]
    assert _brief(env, run_id).title == "Weekly sales dashboard"
    with open_session() as s:
        step = s.scalars(
            select(AgentStep).where(AgentStep.run_id == run_id, AgentStep.agent == "intelligence")
        ).one()
        run = s.get(Run, run_id)
        assert (step.model, step.cost_usd, step.status) == ("fast", 0.0, "done")
        assert run is not None and run.title == "Weekly sales dashboard"
        assert s.get(Project, run.project_id).sector == "logistics"  # pyright: ignore[reportOptionalMemberAccess]


def test_unsupported_feature_dropped_with_warning(client_for, env) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
    names = [f.name for f in _brief(env, run_id).features]
    assert names == ["Weekly sales dashboard", "Quick timing view"]
    warnings = [e for e in load_events(run_id) if e.status == "warning"]
    assert len(warnings) == 1 and "Driver route optimiser" in (warnings[0].message or "")


def test_unsupported_constraint_unconfirmed(client_for, env) -> None:
    with client_for() as client:
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
    confirmed = {c.text: c.confirmed for c in _brief(env, run_id).constraints}
    assert confirmed == {
        "Budget is about ten thousand dollars": True,
        "Must integrate with the legacy SAP system": False,
    }


def test_gate1_changes_makes_v2_with_note(client_for, env) -> None:
    rec = Recorder()
    set_provider(rec)
    try:
        with client_for() as client:
            run_id = create_run(client)
            wait_status(client, run_id, "waiting_gate1")
            body = {"decision": "changes", "note": "budget is 40k, not 4k"}
            assert client.post(GATE.format(run_id, "scope"), json=body).status_code == 200
            wait_status(client, run_id, "waiting_gate1")
    finally:
        set_provider(None)
    assert sorted(a.version for a in _artifacts(run_id)) == [1, 2]
    assert (env / "runs" / run_id / "requirements.v2.json").is_file()
    assert "budget is 40k, not 4k" not in rec.prompts[0]
    assert "budget is 40k, not 4k" in rec.prompts[1]
    assert "<untrusted>" in rec.prompts[1] and "[00:00:01] Alice Smith:" in rec.prompts[1]


def _create(client: Any, name: str, sector: str | None) -> str:
    from tests.graph.conftest import SAMPLE_VTT

    data = {"client": name, **({"sector": sector} if sector else {})}
    files = [("files", ("s.vtt", SAMPLE_VTT.read_bytes(), "text/vtt"))]
    res = client.post("/api/runs", files=files, data=data)
    assert res.status_code == 201, res.text
    return res.json()["id"]


def test_client_and_sector_follow_the_owners_input(client_for, env) -> None:
    with client_for() as client:
        run_id = _create(client, "Acme Retail", "healthcare")  # the mock fixture says "Acme" and logistics
        wait_status(client, run_id, "waiting_gate1")
        brief = _brief(env, run_id)
        assert (brief.client, brief.sector) == ("Acme Retail", "healthcare")
        # Gate 1 identity check: the saved brief round-trips unchanged
        res = client.post(
            GATE.format(run_id, "scope"), json={"decision": "approve", "edits": brief.model_dump(mode="json")}
        )
        assert res.status_code == 200, res.text


def test_extracted_sector_is_kept_when_the_owner_picked_none(client_for, env) -> None:
    with client_for() as client:
        run_id = _create(client, "Acme Retail", None)
        wait_status(client, run_id, "waiting_gate1")
    brief = _brief(env, run_id)
    assert (brief.client, brief.sector) == ("Acme Retail", "logistics")
