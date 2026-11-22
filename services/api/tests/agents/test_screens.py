import json
from pathlib import Path
from typing import Any

from sqlalchemy import select

from poc_studio.db.models import AgentStep, Artifact
from poc_studio.db.session import open_session
from poc_studio.llm import ChatReply
from poc_studio.llm.client import set_provider
from poc_studio.llm.provider import FIXTURE_DIR, MockProvider
from poc_studio.media.assemble import assemble
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.screenpack import ScreenPack
from poc_studio.screens.kits import load_kit
from poc_studio.screens.validate import validate
from tests.graph.conftest import create_run, wait_status

FIXTURES = json.loads((FIXTURE_DIR / "screens.json").read_text(encoding="utf-8"))


class Recorder:
    """Wraps the mock provider and keeps every prompt it was sent, per agent."""

    def __init__(self, fixture_dir: Path = FIXTURE_DIR) -> None:
        self.inner = MockProvider(fixture_dir)
        self.prompts: dict[str, list[str]] = {}

    async def chat(self, model: str, messages: list[dict[str, str]], max_tokens: int, timeout: float,
                   agent: str | None = None) -> ChatReply:  # fmt: skip
        self.prompts.setdefault(agent or "", []).append("\n".join(m["content"] for m in messages))
        return await self.inner.chat(model, messages, max_tokens, timeout, agent)


def _run_to_screens(client_for: Any, rec: Recorder, final: str) -> str:
    set_provider(rec)
    try:
        with client_for() as client:
            run_id = create_run(client)
            wait_status(client, run_id, "waiting_gate1")
            res = client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
            assert res.status_code == 200
            wait_status(client, run_id, final)
            return run_id
    finally:
        set_provider(None)


def test_fixture_is_a_repair_scenario() -> None:
    kit = load_kit("logistics")
    assert isinstance(FIXTURES, list) and len(FIXTURES) == 2
    assert validate(ScreenPack.model_validate(FIXTURES[0]), kit) != []
    assert validate(ScreenPack.model_validate(FIXTURES[1]), kit) == []


def test_graph_run_repairs_and_stores_screenpack(client_for, env) -> None:
    rec = Recorder()
    run_id = _run_to_screens(client_for, rec, "waiting_gate2")
    with open_session() as s:
        arts = list(
            s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "screenpack"))
        )
        step = s.scalars(
            select(AgentStep).where(AgentStep.run_id == run_id, AgentStep.agent == "screens")
        ).one()
    assert [(a.version, a.path.rsplit("/", 1)[1]) for a in arts] == [(1, "screenpack.v1.json")]
    assert step.model == "smart" and step.status == "done"
    pack = ScreenPack.model_validate_json(
        (env / "runs" / run_id / "screenpack.v1.json").read_text(encoding="utf-8")
    )
    assert validate(pack, load_kit("logistics")) == []
    assert len(rec.prompts["screens"]) == 2  # invalid first, then the repaired pack


def test_repair_prompt_names_the_issue_codes(client_for, env) -> None:
    rec = Recorder()
    _run_to_screens(client_for, rec, "waiting_gate2")
    first, second = rec.prompts["screens"]
    assert "<untrusted>" in first and "Acme" in first and "Weekly sales dashboard" in first
    assert "P1" in first and "Example screen `dashboard`" in first and ".pf .lgx" in first
    assert "failed these checks" not in first
    assert "failed these checks" in second
    for code in ("css_scope", "step_css_scope", "undefined_class", "route_format"):
        assert f"[{code}]" in second
    assert "mystery-badge" in second


def test_pack_still_invalid_after_two_repairs_fails_the_step(client_for, env, tmp_path) -> None:
    (tmp_path / "screens.json").write_text(json.dumps(FIXTURES[0]), encoding="utf-8")
    for name in ("intelligence.json", "architect.json"):
        (tmp_path / name).write_text((FIXTURE_DIR / name).read_text(encoding="utf-8"), encoding="utf-8")
    rec = Recorder(tmp_path)
    run_id = _run_to_screens(client_for, rec, "failed")
    assert len(rec.prompts["screens"]) == 3  # first try plus 2 repairs
    with open_session() as s:
        step = s.scalars(
            select(AgentStep).where(AgentStep.run_id == run_id, AgentStep.agent == "screens")
        ).one()
        arts = list(
            s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "screenpack"))
        )
    assert step.status == "failed" and arts == []
    msg = step.error_message or ""
    assert len(msg) <= 500 and "ScreenPack invalid after 2 repairs" in msg and "[css_scope]" in msg


def test_valid_fixture_assembles_into_a_deck() -> None:
    pack = ScreenPack.model_validate(FIXTURES[1])
    plan = DeckPlan.model_validate(_plan_for(pack))
    deck = assemble(pack, plan, None, extra_css=load_kit("logistics").icons_css)
    assert deck.startswith("<!doctype html>")
    for s in pack.screens:
        assert f'id="tpl-{s.id}"' in deck
    for step in (st for sl in plan.slides for st in sl.steps):
        assert any(a.selector == step.spotlight for s in pack.screens for a in s.anchors)


def _plan_for(pack: ScreenPack) -> dict[str, Any]:
    """Minimal DeckPlan: welcome, one area slide per screen, play, close."""
    area = [
        {
            "id": s.id, "kind": "area", "eyebrow": s.label, "title": s.label,
            "caption": f"A look at {s.label}.",
            "steps": [
                {"title": a.purpose, "caption": a.purpose, "spotlight": a.selector} for a in s.anchors[:4]
            ],
        }
        for s in pack.screens
    ]  # fmt: skip
    return {
        "title": "Acme weekly sales prototype",
        "accent": pack.accent,
        "playScreens": [{"id": s.id, "label": s.label} for s in pack.screens if s.play],
        "slides": [
            {
                "id": "welcome",
                "kind": "welcome",
                "title": "Weekly sales, one screen",
                "caption": "A guided tour.",
            },
            *area,
            {"id": "play", "kind": "play", "title": "Try it", "caption": "Click through the prototype."},
            {"id": "close", "kind": "close", "title": "Next steps", "caption": "What we build next."},
        ],
    }


def test_mock_screens_follow_the_chosen_sector_kit(client_for, env) -> None:
    """The owner's sector now decides the kit, so the canned (logistics) reply is re-skinned to it."""
    from tests.graph.conftest import SAMPLE_VTT

    set_provider(Recorder())
    try:
        with client_for() as client:
            res = client.post(
                "/api/runs",
                files=[("files", ("s.vtt", SAMPLE_VTT.read_bytes(), "text/vtt"))],
                data={"client": "Acme", "sector": "fintech"},
            )
            run_id = res.json()["id"]
            wait_status(client, run_id, "waiting_gate1")
            client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
            wait_status(client, run_id, "waiting_gate2")
    finally:
        set_provider(None)
