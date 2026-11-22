"""Assemble (Pitch and Docs, second node): ScreenPack and DeckPlan in, one self-contained deck HTML out."""

from typing import Any

from poc_studio.agents.store import latest_json, next_version, record, slugify
from poc_studio.events import emit
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope
from poc_studio.media.assemble import assemble
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.requirements import Requirements
from poc_studio.schemas.screenpack import ScreenPack
from poc_studio.screens.kits import load_kit, sector_dir

AGENT = "assemble"


async def run_assemble(state: RunState) -> dict[str, Any]:
    run_id = state["run_id"]
    async with step_scope(run_id, AGENT):
        req = latest_json(state, "requirements", Requirements)
        pack = latest_json(state, "screenpack", ScreenPack)
        plan = latest_json(state, "deck", DeckPlan)
        if req is None or pack is None or plan is None:  # screens or pitch did not run (stubbed pipeline)
            emit(run_id, AGENT, "log", message="assemble skipped, no requirements, screenpack or deck plan")
            return {}
        text = " ".join([req.title, req.summary, *(f.name for f in req.features)])
        icons = load_kit(sector_dir(req.sector, text)).icons_css
        html = assemble(
            pack, plan, logo_data_uri=None, extra_css=icons
        )  # DeckNotSelfContained fails the step
        version = next_version(run_id, "deck")
        record(run_id, "deck", version, f"deck/{slugify(req.title)}.v{version}.html", html.encode("utf-8"))
        emit(run_id, AGENT, "log", message=f"deck html v{version}: {len(html) // 1024} KB")
        return {}


NODE = NodeSpec("assemble", run_assemble, "assemble")
