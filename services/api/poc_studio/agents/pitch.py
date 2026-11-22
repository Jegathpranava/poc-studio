"""Pitch and Docs (agent 5): brief, architecture and screenpack in; `deck` plan, docs and .pptx out.

Step 1 plans the deck with a free model and checks it deterministically. Step 2 lets Haiku polish only the
titles and captions, under the budget guard (`BudgetExceeded` propagates, so the run pauses).
"""

import json
import re
from typing import Any

from pydantic import BaseModel

from poc_studio.agents.store import (
    MissingInput,
    latest_json,
    next_version,
    record,
    slugify,
    stub_skip_allowed,
)
from poc_studio.config import get_settings
from poc_studio.db.models import AgentStep, Run
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.revise import clear_note, note_block, rerun_reason, revise_note
from poc_studio.graph.spend import node_budget
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope
from poc_studio.llm import complete_json, wrap_untrusted
from poc_studio.media.docs import exec_summary, user_flows
from poc_studio.media.pptx import build_pptx
from poc_studio.schemas.architecture import Architecture
from poc_studio.schemas.deck import DeckPlan, Figure
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
    "- The `close` slide has 2 to 4 `figures`. Each figure's `value` is a number read from the brief or the "
    "architecture, and `source` is the exact dotted path to it: `brief: <path>` or `architecture: <path>`, "
    "for example `architecture: monthly_cost.total_usd`, `architecture: monthly_cost.lines[0].usd`, "
    "`architecture: phases.weeks` (any phase) or `brief: budget.amount_usd`. The value must equal the number "
    "at that path. Never invent a figure.\n"
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


_SOURCE = re.compile(r"^\s*(brief|architecture)\s*:\s*(\S+)\s*$", re.IGNORECASE)
_SEGMENT = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)(?:\[(\d+)\])?$")
MIN_FIGURES, MAX_FIGURES = 2, 4
FIGURE_CODES = frozenset({"bad_figure_source", "unsupported_figure", "figure_count"})
MAX_LISTED_PATHS = 40
_NOT_FIGURES = frozenset({"confidence"})  # internal extraction scores, not facts for a pitch slide
# Dashes a model may write where a selector needs the ASCII hyphen-minus:
# U+2010-2015, U+2212, U+FE63 and U+FF0D.
_DASHES = str.maketrans(dict.fromkeys("\u2010\u2011\u2012\u2013\u2014\u2015\u2212\ufe63\uff0d", "-"))


def norm_hyphens(s: str) -> str:
    """`[data\u2011anchor="x"]` -> `[data-anchor="x"]`: Unicode dashes become the ASCII hyphen."""
    return s.translate(_DASHES)


def resolve_source(source: str, sources: dict[str, Any]) -> list[float] | None:
    """Numbers at a figure source such as `architecture: monthly_cost.lines[0].usd`.

    A list without an index (`phases.weeks`) fans out over every element. None when the source is not a
    `brief: path` or `architecture: path`, the path misses, or it ends on something that is not a number.
    """
    m = _SOURCE.match(source)
    if m is None or m.group(1).lower() not in sources:
        return None
    nodes: list[Any] = [sources[m.group(1).lower()]]
    for segment in m.group(2).split("."):
        part = _SEGMENT.match(segment)
        if part is None:
            return None
        key, index = part.group(1), part.group(2)
        nxt: list[Any] = []
        for node in nodes:
            for item in node if isinstance(node, list) else [node]:  # a list fans out to its elements
                if isinstance(item, dict) and key in item:
                    value = item[key]
                    if index is None:
                        nxt.append(value)
                    elif isinstance(value, list) and int(index) < len(value):
                        nxt.append(value[int(index)])
        nodes = nxt
    flat = [x for n in nodes for x in (n if isinstance(n, list) else [n])]
    numbers = [float(x) for x in flat if isinstance(x, int | float) and not isinstance(x, bool)]
    return numbers or None


def figure_problem(fig: Figure, sources: dict[str, Any]) -> tuple[str, str] | None:
    """(issue code, message) when the figure does not check out against its source, else None."""
    values = resolve_source(fig.source, sources)
    if values is None:
        return "bad_figure_source", (
            f"figure {fig.label!r}: source {fig.source!r} does not resolve; use "
            "`brief: <dotted.path>` or `architecture: <dotted.path>` that ends on a number"
        )
    if not any(abs(fig.value - v) < 1e-6 for v in values):
        return "unsupported_figure", (
            f"figure {fig.label!r} value {fig.value:g} differs from {fig.source!r} = "
            + ", ".join(f"{v:g}" for v in values)
        )
    return None


def _numeric_leaves(sources: dict[str, Any]) -> list[tuple[str, float, str]]:
    """(source, value, label) for every path in `brief` and `architecture` that `resolve_source` turns into
    exactly one number. The label comes from a sibling `name`/`item`/`label` when the number has one."""
    out: list[tuple[str, float, str]] = []

    def label_for(parent: dict[str, Any], key: str, path: str) -> str:
        unit = "weeks" if key == "weeks" else "USD" if key.endswith("usd") else ""
        named = next((parent[k] for k in ("name", "item", "label") if isinstance(parent.get(k), str)), None)
        words = [p.split("[")[0] for p in path.split(".")[-2:]]
        words[-1] = words[-1].removesuffix("usd").rstrip("_")  # the unit goes in brackets instead
        base = named or " ".join(words).replace("_", " ").strip()
        base = base[:1].upper() + base[1:]
        return f"{base} ({unit})" if unit and unit.lower() not in base.lower() else base

    def walk(node: Any, path: str, root: str) -> None:
        if isinstance(node, dict):
            for key, value in node.items():
                if not _SEGMENT.match(key) or key in _NOT_FIGURES:
                    continue
                sub = f"{path}.{key}" if path else key
                if isinstance(value, int | float) and not isinstance(value, bool):
                    out.append((f"{root}: {sub}", float(value), label_for(node, key, sub)))
                else:
                    walk(value, sub, root)
        elif isinstance(node, list) and path:
            for i, item in enumerate(node):
                if isinstance(item, dict):  # the resolver indexes one level: `lines[0].usd`
                    walk(item, f"{path}[{i}]", root)

    for root in ("architecture", "brief"):
        if isinstance(sources.get(root), dict):
            walk(sources[root], "", root)
    return out


def available_figure_paths(sources: dict[str, Any]) -> list[tuple[str, float]]:
    """Every `brief: ...` / `architecture: ...` source that resolves to a number, with that number."""
    return [(source, value) for source, value, _ in _numeric_leaves(sources)]


def format_figure_paths(sources: dict[str, Any]) -> str:
    paths = available_figure_paths(sources)[:MAX_LISTED_PATHS]
    if not paths:
        return "(none: the brief and architecture hold no numbers)"
    return "\n".join(f"- {source} = {value:g}" for source, value in paths)


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
            allowed = {norm_hyphens(a.selector): a.selector for a in screen.anchors}
            for step in slide.steps:
                exact = allowed.get(norm_hyphens(step.spotlight))
                if exact is None:
                    add(
                        slide.id,
                        "bad_spotlight",
                        f"{step.spotlight!r} is not one of {sorted(allowed.values())}",
                    )
                else:
                    step.spotlight = exact  # a Unicode dash in an otherwise right selector is fixed in place
    for play in plan.play_screens:
        screen = screens.get(play.id)
        if screen is None or not screen.play:
            add(play.id, "bad_play_screen", f"playScreens entry {play.id!r} is not a screen with play=true")
    sources = _sources(req, arch)
    figures = [f for s in plan.slides if s.kind == "close" for f in s.figures]
    if not MIN_FIGURES <= len(figures) <= MAX_FIGURES:
        add("close", "figure_count", f"the close slide needs {MIN_FIGURES} to {MAX_FIGURES} figures")
    for fig in figures:
        problem = figure_problem(fig, sources)
        if problem is not None:
            add("close", *problem)
    return issues


def _sources(req: Requirements, arch: Architecture) -> dict[str, Any]:
    return {"brief": req.model_dump(mode="json"), "architecture": arch.model_dump(mode="json")}


def fallback_figures(plan: DeckPlan, sources: dict[str, Any]) -> list[str]:
    """Last resort when only figure checks still fail after the repairs: keep the figures that check out,
    take the source's number when the path resolves to exactly one, drop the rest, and top up from real
    numeric paths so the close slide has MIN_FIGURES to MAX_FIGURES figures. Returns what changed."""
    close = next((s for s in plan.slides if s.kind == "close"), None)
    if close is None:
        return []
    notes: list[str] = []
    kept: list[Figure] = []
    for fig in close.figures:
        values = resolve_source(fig.source, sources)
        if values is not None and any(abs(fig.value - v) < 1e-6 for v in values):
            kept.append(fig)
        elif values is not None and len(values) == 1:
            notes.append(f"{fig.label!r} value {fig.value:g} -> {values[0]:g}")
            kept.append(fig.model_copy(update={"value": values[0]}))
        else:
            notes.append(f"dropped {fig.label!r} ({fig.source})")
    kept = kept[:MAX_FIGURES]
    used = {" ".join(f.source.split()).lower() for f in kept}
    # Totals first, zeros last: "Monthly cost total 250" makes a better closing figure than one cost line.
    leaves = sorted(_numeric_leaves(sources), key=lambda leaf: ("total" not in leaf[0], leaf[1] == 0))
    for source, value, label in leaves:
        if len(kept) >= MIN_FIGURES:
            break
        if source.lower() not in used:
            kept.append(Figure(label=label, value=value, source=source))
            used.add(source.lower())
            notes.append(f"added {label!r} from {source}")
    close.figures = kept
    return notes


# ---- prompts ---------------------------------------------------------------------------------------------


def build_prompt(pack: ScreenPack, req: Requirements, arch: Architecture, note: str | None = None) -> str:
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
        f"Architecture (JSON), allowed figure source `architecture`:\n{json.dumps(arch_facts, indent=1)}\n\n"
        f"Allowed figure sources (pick {MIN_FIGURES} to {MAX_FIGURES} of these exact paths; "
        "each figure's value must equal the number shown):\n"
        + format_figure_paths(_sources(req, arch))
        + note_block(note)
    )


def repair_prompt(plan: DeckPlan, issues: list[Issue], sources: dict[str, Any] | None = None) -> str:
    paths = ""
    if sources is not None and any(i.code in FIGURE_CODES for i in issues):
        paths = (
            "\n\nAllowed figure sources (use only these exact paths; "
            "each value must equal the number shown):\n" + format_figure_paths(sources)
        )
    return (
        "Your previous deck plan failed these checks:\n"
        + "\n".join(f"- {i}" for i in issues)
        + paths
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
    version = next_version(run_id, "deck", ".json")
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
    """Degrades like port: a failed plan or missing input fails the step (error event), not the run."""
    try:
        return await _run_pitch(state)
    except (DeckPlanInvalid, MissingInput) as exc:  # step_scope already recorded the failure
        return {"deck_result": {"ok": False, "error": str(exc)[:500]}}


async def _run_pitch(state: RunState) -> dict[str, Any]:
    run_id = state["run_id"]
    settings = get_settings()
    reason = rerun_reason(state, AGENT)
    async with step_scope(run_id, AGENT, model=settings.default_fast_model, reason=reason) as step_id:
        req = latest_json(state, "requirements", Requirements)
        arch = latest_json(state, "architecture", Architecture)
        pack = latest_json(state, "screenpack", ScreenPack)
        missing = [
            n for n, v in (("requirements", req), ("architecture", arch), ("screenpack", pack)) if v is None
        ]
        if req is None or arch is None or pack is None:
            if not stub_skip_allowed():  # a real run: fail the step, the run still reaches Gate 2
                raise MissingInput(f"pitch needs the {', '.join(missing)} artifact")
            emit(run_id, AGENT, "log", message=f"pitch skipped, no {', '.join(missing)} artifact")
            return {}
        budget = node_budget(state)
        tokens_in = tokens_out = 0
        try:
            user = build_prompt(pack, req, arch, revise_note(state, AGENT))
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
                user = repair_prompt(plan, issues, _sources(req, arch))
            if plan is not None and issues and all(i.code in FIGURE_CODES for i in issues):
                notes = fallback_figures(plan, _sources(req, arch))  # the rest of the deck is fine: keep it
                issues = check_plan(plan, pack, req, arch)
                if not issues:
                    emit(run_id, AGENT, "log", message="figures taken from the sources: " + "; ".join(notes))
            if issues or plan is None:
                raise DeckPlanInvalid(issues)
            plan.accent, plan.logo = pack.accent, ""
            plan.byline = plan.byline or "Prepared by PoC Studio"
            sources = _sources(req, arch)
            for fig in (f for s in plan.slides for f in s.figures):
                fig.verified = figure_problem(fig, sources) is None  # True only when its source resolved
            if state.get("free_polish"):  # the owner chose the free model at a budget pause
                emit(run_id, AGENT, "log", message="polish skipped: titles and captions stay as drafted")
            else:
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
        return {
            "deck": plan.model_dump(mode="json", by_alias=True),
            "deck_result": {"ok": True},
            "spent_delta": budget.charged_usd,
            **clear_note(state, AGENT),
        }


NODE = NodeSpec("pitch", run_pitch, "pitch")
