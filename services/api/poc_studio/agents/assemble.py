"""Assemble (Pitch and Docs, second node): ScreenPack and DeckPlan in, one self-contained deck HTML out."""

from typing import Any

from poc_studio.agents.store import (
    MissingInput,
    latest_json,
    next_version,
    record,
    slugify,
    stub_skip_allowed,
)
from poc_studio.events import emit
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope
from poc_studio.media.assemble import DeckNotSelfContained, assemble
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.requirements import Requirements
from poc_studio.schemas.screenpack import ScreenPack
from poc_studio.screens.kits import load_kit, sector_dir

AGENT = "assemble"


async def run_assemble(state: RunState) -> dict[str, Any]:
    """Degrades like port: no plan, no pack or an unsafe deck fails the step; the run still reaches Gate 2."""
    try:
        return await _run_assemble(state)
    except (MissingInput, DeckNotSelfContained) as exc:  # step_scope already recorded the failure
        return {"deck_result": {"ok": False, "error": str(exc)[:500]}}


async def _run_assemble(state: RunState) -> dict[str, Any]:
    run_id = state["run_id"]
    async with step_scope(run_id, AGENT):
        req = latest_json(state, "requirements", Requirements)
        pack = latest_json(state, "screenpack", ScreenPack)
        plan = latest_json(state, "deck", DeckPlan)
        if req is None or pack is None or plan is None:
            if not stub_skip_allowed():
                raise MissingInput("assemble needs the requirements, screenpack and deck plan artifacts")
            emit(run_id, AGENT, "log", message="assemble skipped, no requirements, screenpack or deck plan")
            return {}
        text = " ".join([req.title, req.summary, *(f.name for f in req.features)])
        icons = load_kit(sector_dir(req.sector, text)).icons_css
        html = assemble(
            pack, plan, logo_data_uri=None, extra_css=icons
        )  # DeckNotSelfContained fails the step
        version = next_version(run_id, "deck", ".html")
        record(run_id, "deck", version, f"deck/{slugify(req.title)}.v{version}.html", html.encode("utf-8"))
        emit(run_id, AGENT, "log", message=f"deck html v{version}: {len(html) // 1024} KB")
        return {"deck_result": {"ok": True}}


NODE = NodeSpec("assemble", run_assemble, "assemble")
