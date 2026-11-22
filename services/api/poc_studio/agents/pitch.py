"""Pitch and Docs (agent 5): brief, architecture and screenpack in; `deck` plan, docs and .pptx out.

Step 1 plans the deck with a free model and checks it deterministically. Step 2 lets Haiku polish only the
titles and captions, under the budget guard (`BudgetExceeded` propagates, so the run pauses).
"""

import json
import re
from typing import Any

from pydantic import BaseModel

from poc_studio.agents.store import latest_json, next_version, record, slugify
from poc_studio.config import get_settings
from poc_studio.db.models import AgentStep, Run
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.spend import node_budget
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope
from poc_studio.llm import complete_json, wrap_untrusted
from poc_studio.media.docs import exec_summary, user_flows
from poc_studio.media.pptx import build_pptx
from poc_studio.schemas.architecture import Architecture
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.requirements import Requirements
from poc_studio.schemas.screenpack import ScreenPack
from poc_studio.screens.validate import Issue

AGENT = "pitch"
POLISH_AGENT = "pitch_polish"
MAX_TOKENS = 8000
POLISH_MAX_TOKENS = 3000
MAX_REPAIRS = 2

DeckPlanDraft = DeckPlan  # the model drafts the plan; the docs fields stay empty until we fill them

SYSTEM = (
    "You are the Pitch and Docs agent. Write the slide plan of a short guided product tour as JSON.\n\n"
    "Rules:\n"
    "- 9 to 12 slides in this order: one `welcome`, at most one `overview`, `area` slides, one `play`, "
    "one `close`.\n"
    "- The `overview` slide and every `area` slide use the id of a real screen (listed in the prompt): one "
    "area slide per key screen. Never invent a screen id. `welcome`, `play` and `close` use ids "
    "`welcome`, `play`, `close`.\n"
    "- Each `area` slide has 3 to 5 steps; the `overview` slide is a tour of its screen. Every step "
    "`spotlight` is copied exactly from that screen's anchor selectors.\n"
    "- `playScreens` lists screens marked play=true, with their id and label.\n"
    "- The `close` slide has 2 to 4 `figures`. Each figure's `value` is a number that appears in the brief "
    "or the architecture, and `source` names where: `brief: <field>` or `architecture: <field>` "
    "(for example `architecture: monthly_cost.total_usd`). Never invent a figure.\n"
    "- Titles are short; captions are one plain sentence. Do not claim anything the brief does not support."
)

POLISH_SYSTEM = (
    "You polish slide wording. Reply with the same ids. Make each title and caption clearer and more "
    "persuasive for an executive reader without changing the facts, numbers or meaning. Keep every "
    "caption to one sentence."
)


class Polished(BaseModel):
    title: str | None = None
    caption: str | None = None


class PolishedSlide(Polished):
    id: str
    steps: list[Polished] = []


class PolishPatch(BaseModel):
    slides: list[PolishedSlide]


class DeckPlanInvalid(RuntimeError):
    def __init__(self, issues: list[Issue]) -> None:
        self.issues = issues
        super().__init__(
            f"Deck plan invalid after {MAX_REPAIRS} repairs, {len(issues)} issues: "
            + "; ".join(str(i) for i in issues)
        )


# ---- deterministic checks ------------------------------------------------------------------------------


def _numbers(data: Any) -> list[float]:
    if isinstance(data, bool):
        return []
    if isinstance(data, int | float):
        return [float(data)]
    if isinstance(data, str):
        return [float(m.replace(",", "")) for m in re.findall(r"\d[\d,]*(?:\.\d+)?", data)]
    if isinstance(data, dict):
        return [n for v in data.values() for n in _numbers(v)]
    if isinstance(data, list):
        return [n for v in data for n in _numbers(v)]
    return []


def _keys(data: Any) -> set[str]:
    if isinstance(data, dict):
        return {str(k).lower() for k in data} | {k for v in data.values() for k in _keys(v)}
    if isinstance(data, list):
        return {k for v in data for k in _keys(v)}
    return set()


def check_plan(plan: DeckPlan, pack: ScreenPack, req: Requirements, arch: Architecture) -> list[Issue]:
    issues: list[Issue] = []

    def add(slide_id: str | None, code: str, message: str) -> None:
        issues.append(Issue(screen_id=slide_id, code=code, message=message))

    screens = {s.id: s for s in pack.screens}
    for slide in plan.slides:
        if slide.kind in ("overview", "area"):
            screen = screens.get(slide.id)
            if screen is None:
                add(
                    slide.id, "unknown_screen", f"slide id {slide.id!r} is not a screen id: {sorted(screens)}"
                )
                continue
            allowed = {a.selector for a in screen.anchors}
            for step in slide.steps:
                if step.spotlight not in allowed:
                    add(slide.id, "bad_spotlight", f"{step.spotlight!r} is not one of {sorted(allowed)}")
    for play in plan.play_screens:
        screen = screens.get(play.id)
        if screen is None or not screen.play:
            add(play.id, "bad_play_screen", f"playScreens entry {play.id!r} is not a screen with play=true")
    sources = {"brief": req.model_dump(mode="json"), "architecture": arch.model_dump(mode="json")}
    for fig in (f for s in plan.slides for f in s.figures):
        text = fig.source.lower()
        named = [name for name in sources if name in text]
        if not named:
            add("close", "bad_figure_source", f"figure {fig.label!r}: source must name brief or architecture")
            continue
        tokens = set(re.findall(r"[a-z_0-9]+", text)) - set(sources)
        if not any(tokens & _keys(sources[n]) for n in named):
            add("close", "bad_figure_source", f"figure {fig.label!r}: source names no field of {named}")
        if not any(abs(fig.value - n) < 1e-6 for name in named for n in _numbers(sources[name])):
            add("close", "unsupported_figure", f"figure {fig.label!r} value {fig.value:g} not in {named}")
    return issues


# ---- prompts ---------------------------------------------------------------------------------------------


def build_prompt(pack: ScreenPack, req: Requirements, arch: Architecture) -> str:
    screens = [
        {"id": s.id, "label": s.label, "play": s.play, "anchors": [a.selector for a in s.anchors]}
        for s in pack.screens
    ]
    brief = req.model_dump(
        mode="json", include={"client", "title", "summary", "goals", "pain_points", "budget", "timeline"}
    )
    brief["features"] = [{"name": f.name, "priority": f.priority} for f in req.features]
    arch_facts = {
        "monthly_cost": arch.monthly_cost.model_dump(mode="json"),
        "phases": [p.model_dump(mode="json") for p in arch.phases],
        "models": [m.model_dump(mode="json") for m in arch.models],
        "components": [c.name for c in arch.components],
    }
    return (
        f"Client: {req.client}. Accent colour: {pack.accent}.\n\n"
        "Screens (ids, labels and the only allowed spotlight selectors):\n"
        f"{json.dumps(screens, indent=1)}\n\n"
        "Brief (JSON), allowed figure source `brief`:\n"
        + wrap_untrusted(json.dumps(brief, indent=1))
        + "\n\n"
        f"Architecture (JSON), allowed figure source `architecture`:\n{json.dumps(arch_facts, indent=1)}"
    )


def repair_prompt(plan: DeckPlan, issues: list[Issue]) -> str:
    return (
        "Your previous deck plan failed these checks:\n"
        + "\n".join(f"- {i}" for i in issues)
        + f"\n\nPrevious plan JSON:\n{plan.model_dump_json(by_alias=True)}\n\n"
        "Return the complete corrected plan as one JSON object. Fix every issue, keep everything else."
    )


def polish_input(plan: DeckPlan) -> str:
    """Only titles and captions, as compact JSON."""
    return json.dumps(
        {
            "slides": [
                {
                    "id": s.id, "title": s.title, "caption": s.caption,
                    "steps": [{"title": st.title, "caption": st.caption} for st in s.steps],
                }
                for s in plan.slides
            ]
        },
        separators=(",", ":"),
    )  # fmt: skip


def _pick(new: str | None, old: str) -> str:
    return new.strip() if new and new.strip() else old


def apply_patch(plan: DeckPlan, patch: PolishPatch) -> DeckPlan:
    """Apply by slide id (steps by position); unknown ids and empty values are ignored."""
    by_id = {p.id: p for p in patch.slides}
    for slide in plan.slides:
        p = by_id.get(slide.id)
        if p is None:
            continue
        slide.title, slide.caption = _pick(p.title, slide.title), _pick(p.caption, slide.caption)
        for step, sp in zip(slide.steps, p.steps, strict=False):
            step.title, step.caption = _pick(sp.title, step.title), _pick(sp.caption, step.caption)
    return plan


# ---- persistence ----------------------------------------------------------------------------------------


def _write_outputs(run_id: str, plan: DeckPlan, pack: ScreenPack, req: Requirements) -> int:
    version = next_version(run_id, "deck")
    plan_json = plan.model_dump_json(by_alias=True, indent=2).encode()
    record(run_id, "deck", version, f"deck/plan.v{version}.json", plan_json)
    dv = next_version(run_id, "docs")
    record(run_id, "docs", dv, f"docs/exec-summary.v{dv}.md", plan.exec_summary_md.encode())
    record(run_id, "docs", dv, f"docs/user-flows.v{dv}.md", plan.user_flows_md.encode())
    pv = next_version(run_id, "pptx")
    name = f"{slugify(req.title)}.v{pv}.pptx"
    tmp = get_settings().runs_dir / run_id / "deck" / name
    build_pptx(plan, pack, tmp)  # writes the file; `record` stores the bytes under the same path
    record(run_id, "pptx", pv, f"deck/{name}", tmp.read_bytes())
    return version


# ---- node ------------------------------------------------------------------------------------------------


async def run_pitch(state: RunState) -> dict[str, Any]:
    run_id = state["run_id"]
    settings = get_settings()
    async with step_scope(run_id, AGENT, model=settings.default_fast_model) as step_id:
        req = latest_json(state, "requirements", Requirements)
        arch = latest_json(state, "architecture", Architecture)
        pack = latest_json(state, "screenpack", ScreenPack)
        missing = [
            n for n, v in (("requirements", req), ("architecture", arch), ("screenpack", pack)) if v is None
        ]
        if req is None or arch is None or pack is None:  # upstream stubbed or not run: nothing to pitch
            emit(run_id, AGENT, "log", message=f"pitch skipped, no {', '.join(missing)} artifact")
            return {}
        budget = node_budget(state)
        tokens_in = tokens_out = 0
        try:
            user = build_prompt(pack, req, arch)
            plan: DeckPlan | None = None
            issues: list[Issue] = []
            for attempt in range(MAX_REPAIRS + 1):
                res = await complete_json(
                    agent=AGENT, model=settings.default_fast_model, system=SYSTEM, user=user,
                    schema=DeckPlanDraft, max_tokens=MAX_TOKENS, run=budget,
                )  # fmt: skip
                tokens_in, tokens_out = tokens_in + res.tokens_in, tokens_out + res.tokens_out
                plan = res.value
                issues = check_plan(plan, pack, req, arch)
                if not issues:
                    break
                emit(run_id, AGENT, "log", message=f"deck plan attempt {attempt + 1}: {len(issues)} issues")
                user = repair_prompt(plan, issues)
            if issues or plan is None:
                raise DeckPlanInvalid(issues)
            plan.accent, plan.logo = pack.accent, ""
            plan.byline = plan.byline or "Prepared by PoC Studio"
            for fig in (f for s in plan.slides for f in s.figures):
                fig.verified = True  # check_plan found its value in the named source
            polished = await complete_json(
                agent=POLISH_AGENT, model=settings.polish_model, system=POLISH_SYSTEM,
                user=polish_input(plan), schema=PolishPatch, max_tokens=POLISH_MAX_TOKENS, run=budget,
            )  # fmt: skip
            tokens_in, tokens_out = tokens_in + polished.tokens_in, tokens_out + polished.tokens_out
            plan = apply_patch(plan, polished.value)
            plan.exec_summary_md = exec_summary(req, arch, plan)
            plan.user_flows_md = user_flows(pack, plan)
            version = _write_outputs(run_id, plan, pack, req)
        finally:
            with open_session() as session:
                row = session.get(AgentStep, step_id)
                if row is not None:
                    row.tokens_in, row.tokens_out, row.cost_usd = tokens_in, tokens_out, budget.charged_usd
                run = session.get(Run, run_id)
                if run is not None:
                    run.tokens_total += tokens_in + tokens_out
                session.commit()
        emit(
            run_id, AGENT, "cost", model=settings.polish_model, tokens_in=tokens_in,
            tokens_out=tokens_out, cost_usd=budget.charged_usd,
        )  # fmt: skip
        emit(run_id, AGENT, "log", message=f"deck plan v{version}: {len(plan.slides)} slides")
        return {"deck": plan.model_dump(mode="json", by_alias=True), "spent_delta": budget.charged_usd}


NODE = NodeSpec("pitch", run_pitch, "pitch")
