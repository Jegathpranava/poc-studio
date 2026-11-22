"""Executive summary and user flows as Markdown. Deterministic: built from the approved artifacts, no LLM."""

from poc_studio.schemas.architecture import Architecture
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.requirements import Requirements
from poc_studio.schemas.screenpack import ScreenPack


def exec_summary(req: Requirements, arch: Architecture, plan: DeckPlan) -> str:
    """One page: problem, solution, cost, next steps."""
    out = [
        f"# {plan.title}: executive summary",
        "",
        f"Prepared for {req.client}.",
        "",
        "## Problem",
        "",
        req.summary,
    ]
    out += [f"- {p}" for p in req.pain_points]
    out += ["", "## Solution", "", arch.rationale, ""]
    out += [f"- {c.name}: {c.detail}" for c in arch.components]
    out += ["", "## What you will see", ""]
    out += [f"- {s.title}: {s.caption}" for s in plan.slides if s.kind in ("overview", "area")]
    cost = arch.monthly_cost
    out += ["", "## Cost", "", f"Estimated running cost: **${cost.total_usd:,.2f} per month**.", ""]
    out += [f"- {line.item}: ${line.usd:,.2f}" for line in cost.lines]
    out += ["", f"Assumptions: {cost.assumptions}"]
    if req.budget.text or req.budget.amount_usd is not None:
        out += ["", f"Client budget: {req.budget.text or f'${req.budget.amount_usd:,.0f}'}."]
    out += ["", "## Next steps", ""]
    if arch.phases:
        out += [f"{i}. {p.name} ({p.weeks:g} wk): {p.detail}" for i, p in enumerate(arch.phases, 1)]
    out += [f"- {a.text}" + (f" ({a.owner})" if a.owner else "") for a in req.action_items]
    return "\n".join(out) + "\n"


def user_flows(pack: ScreenPack, plan: DeckPlan) -> str:
    """One flow per play screen, its steps taken from the matching slide (or the screen anchors)."""
    slides = {s.id: s for s in plan.slides}
    out = [f"# {plan.title}: user flows", ""]
    screens = {s.id: s for s in pack.screens}
    for play in plan.play_screens:
        screen = screens.get(play.id)
        if screen is None:
            continue
        out += [f"## {play.label}", "", f"Route: `{screen.route}`", ""]
        slide = slides.get(play.id)
        if slide is not None and slide.steps:
            out += [f"{i}. **{s.title}**: {s.caption}" for i, s in enumerate(slide.steps, 1)]
        else:
            out += [f"{i}. {a.purpose}" for i, a in enumerate(screen.anchors, 1)]
        out.append("")
    return "\n".join(out).rstrip() + "\n"
