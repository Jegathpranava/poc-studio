import json
from pathlib import Path
from typing import Any

import pytest
from pptx import Presentation
from sqlalchemy import select

from poc_studio.agents.pitch import PolishPatch, apply_patch, check_plan, polish_input
from poc_studio.db.models import AgentStep, Artifact
from poc_studio.db.session import open_session
from poc_studio.llm import BudgetExceeded, RunBudget
from poc_studio.llm.client import complete_json, set_provider
from poc_studio.llm.provider import FIXTURE_DIR
from poc_studio.media.docs import exec_summary, user_flows
from poc_studio.media.pptx import build_pptx
from poc_studio.schemas.architecture import Architecture
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.requirements import Requirements
from poc_studio.schemas.screenpack import ScreenPack
from tests.agents.test_screens import Recorder
from tests.graph.conftest import SAMPLE_VTT, wait_status


def _load(name: str) -> Any:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


PLANS = _load("pitch.json")
PACK = ScreenPack.model_validate(_load("screens.json")[-1])
REQ = Requirements.model_validate(_load("intelligence.json"))
ARCH = Architecture.model_validate(_load("architect.json"))


def plan(index: int = 1) -> DeckPlan:
    return DeckPlan.model_validate(PLANS[index])


def codes(p: DeckPlan) -> set[str]:
    return {i.code for i in check_plan(p, PACK, REQ, ARCH)}


def test_valid_plan_passes_and_has_the_required_shape() -> None:
    p = plan()
    assert check_plan(p, PACK, REQ, ARCH) == []
    assert 9 <= len(p.slides) <= 12
    assert {s.kind for s in p.slides} == {"welcome", "overview", "area", "play", "close"}


def test_invalid_fixture_is_detected() -> None:
    assert codes(plan(0)) == {"unknown_screen", "unsupported_figure"}


def test_each_issue_type() -> None:
    p = plan()
    p.slides[2].id = "nope"
    assert codes(p) == {"unknown_screen"}

    p = plan()
    p.slides[2].steps[0].spotlight = '[data-anchor="made-up"]'
    assert codes(p) == {"bad_spotlight"}

    p = plan()
    p.play_screens[0].id = "products"  # a real screen, but play=false
    assert codes(p) == {"bad_play_screen"}
    p.play_screens[0].id = "ghost"
    assert codes(p) == {"bad_play_screen"}

    p = plan()
    p.slides[-1].figures[1].value = 46
    assert codes(p) == {"unsupported_figure"}

    p = plan()
    p.slides[-1].figures[1].source = "my guess"
    assert codes(p) == {"bad_figure_source"}
    p.slides[-1].figures[1].source = "architecture: vibes"
    assert "bad_figure_source" in codes(p)


def test_figure_number_matches_numerically_and_source_text_loosely() -> None:
    p = plan()
    p.slides[-1].figures[0].value = 10000.0
    p.slides[-1].figures[0].source = "Brief (budget.amount_usd)"  # the brief budget is 10000
    assert codes(p) == set()


def test_polish_patch_applies_by_id_and_ignores_unknown() -> None:
    p = plan()
    before = p.model_dump()
    out = apply_patch(p, PolishPatch.model_validate(_load("pitch_polish.json")))
    assert out.slides[0].title == "Weekly sales, finally in one view"
    assert out.slides[1].steps[0].caption == "Your place in the app is always highlighted."
    assert out.slides[1].steps[0].title == before["slides"][1]["steps"][0]["title"]
    assert out.slides[2].title == "Which regions lead the week"
    assert [s.id for s in out.slides] == [s["id"] for s in before["slides"]]
    assert "Not a real slide" not in out.model_dump_json()
    assert out.slides[-1].figures == plan().slides[-1].figures


def test_polish_input_holds_only_titles_and_captions() -> None:
    text = polish_input(plan())
    data = json.loads(text)
    assert set(data["slides"][1]) == {"id", "title", "caption", "steps"}
    assert set(data["slides"][1]["steps"][0]) == {"title", "caption"}
    assert "spotlight" not in text and "figures" not in text


@pytest.mark.asyncio
async def test_polish_raises_budget_exceeded_on_a_tenth_of_a_cent() -> None:
    rec = Recorder()
    with pytest.raises(BudgetExceeded):
        await complete_json(
            agent="pitch_polish", model="claude-haiku-5-5", system="s", user=polish_input(plan()),
            schema=PolishPatch, max_tokens=3000, run=RunBudget("r", 0.001), provider=rec,
        )  # fmt: skip
    assert rec.prompts == {}  # the guard fires before any call


def _run(client_for: Any, rec: Recorder, final: str, **form: str) -> str:
    set_provider(rec)
    try:
        with client_for() as client:
            res = client.post(
                "/api/runs",
                files=[("files", ("sample.vtt", SAMPLE_VTT.read_bytes(), "text/vtt"))],
                data={"client": "Acme", "sector": "logistics", **form},
            )
            run_id = res.json()["id"]
            wait_status(client, run_id, "waiting_gate1")
            client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
            wait_status(client, run_id, final)
            return run_id
    finally:
        set_provider(None)


def test_graph_run_repairs_polishes_and_stores_outputs(client_for, env) -> None:
    rec = Recorder()
    run_id = _run(client_for, rec, "waiting_gate2")
    first, second = rec.prompts["pitch"]
    assert "weekly-report" in first and "report-steps" in first and "<untrusted>" in first
    assert "failed these checks" not in first and "failed these checks" in second
    assert "[unknown_screen]" in second and "[unsupported_figure]" in second
    assert len(rec.prompts["pitch_polish"]) == 1
    assert "spotlight" not in rec.prompts["pitch_polish"][0].split("Reply with a single JSON")[0]
    with open_session() as s:
        arts = list(s.scalars(select(Artifact).where(Artifact.run_id == run_id)))
        step = s.scalars(
            select(AgentStep).where(AgentStep.run_id == run_id, AgentStep.agent == "pitch")
        ).one()
    names = {a.type: [] for a in arts}
    for a in arts:
        names[a.type].append(a.path.rsplit("/", 1)[1])
    assert any(n.endswith(".pptx") for n in names["pptx"])
    assert sorted(names["docs"]) == ["exec-summary.v1.md", "user-flows.v1.md"]
    saved = DeckPlan.model_validate_json((env / "runs" / run_id / "deck" / "plan.v1.json").read_text("utf-8"))
    assert saved.slides[0].title == "Weekly sales, finally in one view"  # polish applied
    assert all(f.verified for f in saved.slides[-1].figures)
    assert "Acme" in saved.exec_summary_md and saved.user_flows_md
    assert step.status == "done"


def test_run_goes_to_paused_budget_when_polish_does_not_fit(client_for, env) -> None:
    rec = Recorder()
    run_id = _run(client_for, rec, "paused_budget", budget_usd="0.001")
    assert "pitch_polish" not in rec.prompts  # the guard stopped it before the call
    with open_session() as s:
        step = s.scalars(
            select(AgentStep).where(AgentStep.run_id == run_id, AgentStep.agent == "pitch")
        ).one()
        decks = list(s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "deck")))
    assert step.status == "paused" and decks == []


def test_pptx_has_one_slide_per_plan_slide(tmp_path: Path) -> None:
    p = plan()
    out = build_pptx(p, PACK, tmp_path / "deck.pptx")
    prs = Presentation(str(out))
    assert len(prs.slides) == len(p.slides)
    assert (prs.slide_width or 0) / (prs.slide_height or 1) == pytest.approx(16 / 9, abs=0.01)
    close_text = " ".join(sh.text_frame.text for sh in prs.slides[-1].shapes if sh.has_text_frame)  # pyright: ignore
    assert "25" in close_text and "45" in close_text


def test_docs_name_the_client_and_the_cost() -> None:
    p = plan()
    summary = exec_summary(REQ, ARCH, p)
    assert "Acme" in summary and "$45.00" in summary
    for heading in ("## Problem", "## Solution", "## Cost", "## Next steps"):
        assert heading in summary
    flows = user_flows(PACK, p)
    for play in p.play_screens:
        assert f"## {play.label}" in flows
    assert "Compare regions" in flows
