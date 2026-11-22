"""Small QA inputs built from the mock LLM fixtures (intelligence, architect, screens, pitch)."""

import json
from pathlib import Path
from typing import Any

import pytest

from poc_studio.llm.provider import FIXTURE_DIR
from poc_studio.media.assemble import assemble
from poc_studio.media.docs import exec_summary, user_flows
from poc_studio.qa.checks import QAInputs
from poc_studio.schemas.architecture import Architecture
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.requirements import Requirements
from poc_studio.schemas.screenpack import ScreenPack


def _last(name: str) -> dict[str, Any]:
    data = json.loads((Path(FIXTURE_DIR) / f"{name}.json").read_text(encoding="utf-8"))
    return data[-1] if isinstance(data, list) else data


@pytest.fixture
def good() -> QAInputs:
    req = Requirements.model_validate(_last("intelligence"))
    arch = Architecture.model_validate(_last("architect"))
    pack = ScreenPack.model_validate(_last("screens"))
    plan = DeckPlan.model_validate(_last("pitch"))
    for fig in (f for s in plan.slides for f in s.figures):
        fig.verified = True
    plan.exec_summary_md = exec_summary(req, arch, plan)
    plan.user_flows_md = user_flows(pack, plan)
    return QAInputs(
        req=req, arch=arch, pack=pack, plan=plan, deck_html=assemble(pack, plan, None), build={"ok": True}
    )
