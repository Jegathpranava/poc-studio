"""Prototype Builder, part 1 (agent 3): requirements and architecture in, a validated `screenpack` out."""

import hashlib
import json
import re
from typing import Any

from pydantic import BaseModel
from sqlalchemy import func, select

from poc_studio.config import get_settings
from poc_studio.db.models import AgentStep, Artifact, Run
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.revise import clear_note, note_block, rerun_reason, revise_note
from poc_studio.graph.spend import node_budget
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope
from poc_studio.llm import complete_json, wrap_untrusted
from poc_studio.schemas.architecture import Architecture
from poc_studio.schemas.requirements import Requirements
from poc_studio.schemas.screenpack import ScreenPack
from poc_studio.screens.kits import Kit, load_kit, sector_dir
from poc_studio.screens.validate import Issue, validate

AGENT = "screens"
MAX_TOKENS = 16000  # shared by the model's hidden reasoning and the JSON; 8000 left no room for the answer
MAX_REPAIRS = 2
TIMEOUT_S = 300.0  # a full pack from the smart reasoning model can take minutes
REASONING_EFFORT = "low"  # the pack is mostly markup; long reasoning only eats the token allowance
TRUNCATED_NOTE = (
    "Your previous JSON response was cut off because it was too long. Make all HTML fragments much "
    "shorter and use at most 2 table rows per screen. Leave the kit CSS out of `product_css`."
)

SYSTEM = (
    "You are the Prototype Builder agent. Write the product screens of a clickable sector prototype as a "
    "ScreenPack, starting from the sector design kit you are given.\n\nRules:\n"
    "- Keep screens focused and concise: write exactly 6 essential screens (the fewest the schema accepts) "
    'as HTML fragments. Each fragment is rooted at `<div class="<app_class>">`. '
    "Use only classes defined in the kit CSS or in the CSS you add. Icons are "
    '`<span class="ic ic-<name>"></span>` with the names the kit lists.\n'
    "- Keep each screen HTML fragment compact (under 25 to 35 lines of clean HTML).\n"
    "- Tables, lists and cards contain at most 2 sample items or rows. Never generate large data tables.\n"
    "- Keep mock text short and concise. Avoid repetitive markup so the entire ScreenPack fits comfortably "
    "in under 3,000 tokens.\n"
    "- `app_class` and `accent` are the kit's values. The kit's product.css is applied for you: never repeat "
    "it. `product_css` holds only the rules you add (usually none, so an empty string); every rule is "
    "scoped under `.pf .<app_class>`.\n"
    '- `step_css` holds only rules that start with `.pf.sl-<screen id>[data-step="N"]`. It may be empty.\n'
    "- `route` is `/` for exactly one home screen, otherwise `/` plus a kebab-case slug. Routes are unique.\n"
    '- Every screen has 3 to 8 anchors. Each anchor selector is `[data-anchor="<name>"]` and must match '
    "an element in that screen's HTML; names are unique per screen. Anchor what a viewer should look at.\n"
    "- Set `play: true` on at least 3 screens that a visitor can click through; give them realistic states.\n"
    "- Every P1 feature of the brief must be visible on at least one screen; cover P2 where they fit.\n"
    "- No `<script>`, `<iframe>`, `<form>`, `<link>`, `<meta>`, `<style>`, `on*` attributes, inline styles, "
    "external URLs, fonts or images. `script` is null unless a tiny local interaction needs it, and it "
    "never makes network calls.\n"
    "- All data is fictional: invented people, `example.com` addresses, realistic sector numbers. Never use "
    "real people or real companies. The client's name may appear as the product or company name.\n"
    "- Never invent facts about the client that the brief does not support.\n"
    "- Inside HTML fragments, quote every attribute with single quotes (`<div class='card' "
    "data-anchor='totals'>`), never double quotes, so the JSON strings need no escaping. Anchor selectors "
    'keep the `[data-anchor="<name>"]` form.\n'
    "- Output valid JSON directly, with no preamble."
)

_ORDER = {"P1": 0, "P2": 1, "P3": 2}


class ScreenPackInvalid(RuntimeError):
    """The pack still has validation issues after the repairs."""

    def __init__(self, issues: list[Issue]) -> None:
        self.issues = issues
        super().__init__(
            f"ScreenPack invalid after {MAX_REPAIRS} repairs, {len(issues)} issues: "
            + "; ".join(str(i) for i in issues)
        )


def format_issues(issues: list[Issue]) -> str:
    return "\n".join(f"- {i}" for i in issues)


_DQ_ATTR = re.compile(r"""(\s[\w:.-]+)="([^"']*)\"""")


def single_quoted(html: str) -> str:
    """`a="b"` to `a='b'`: the examples then show the quoting the model must use inside JSON strings."""
    return _DQ_ATTR.sub(r"\1='\2'", html)


def build_prompt(req: Requirements, arch: Architecture | None, kit: Kit, note: str | None = None) -> str:
    features = sorted(req.features, key=lambda f: _ORDER[f.priority])
    brief = {
        "client": req.client,
        "title": req.title,
        "summary": req.summary,
        "goals": req.goals,
        "pain_points": req.pain_points,
        "features_ranked": [{"priority": f.priority, "name": f.name, "detail": f.detail} for f in features],
    }
    if arch is not None:
        brief["architecture"] = {
            "use_case_class": arch.use_case_class,
            "components": [{"name": c.name, "kind": c.kind} for c in arch.components],
        }
    examples = "\n\n".join(
        f"Example screen `{ex.id}` ({ex.label}); anchors: "
        + ", ".join(f'[data-anchor="{a}"]' for a in ex.anchors)
        + f"\n```html\n{single_quoted(ex.html.strip())}\n```"
        for ex in kit.examples[:2]
    )
    p1 = [f.name for f in features if f.priority == "P1"]
    return (
        f"Client: {req.client}\n"
        f"Sector kit: {kit.sector}; app_class `{kit.app_class}`; accent `{kit.accent}`.\n"
        f"Every P1 feature needs at least one screen: {', '.join(p1) or 'none'}.\n\n"
        "Brief (JSON):\n\n" + wrap_untrusted(json.dumps(brief, indent=2)) + "\n\n"
        "Kit product.css (already applied; do not repeat it, put only new rules in `product_css`):\n"
        f"```css\n{kit.product_css}\n```\n\n"
        f"Kit selector guide:\n{kit.selectors_md}\n\n{examples}" + note_block(note)
    )


def with_kit_css(pack: ScreenPack, kit: Kit) -> ScreenPack:
    """The model returns only its added rules; the stored pack carries the kit CSS in front of them.
    A model that copied the kit CSS anyway is left as it is."""
    if kit.product_css.strip() in pack.product_css:
        return pack
    return pack.model_copy(update={"product_css": f"{kit.product_css}\n{pack.product_css}".rstrip() + "\n"})


def _added_css(pack: ScreenPack, kit: Kit) -> str:
    return pack.product_css.replace(kit.product_css.strip(), "", 1).strip()


def repair_prompt(pack: ScreenPack, issues: list[Issue], kit: Kit) -> str:
    lean = pack.model_copy(update={"product_css": _added_css(pack, kit)})  # never echo the kit CSS back
    return (
        "Your previous ScreenPack failed these checks:\n"
        f"{format_issues(issues)}\n\n"
        "Previous ScreenPack JSON (kit CSS left out of `product_css`):\n"
        f"{lean.model_dump_json()}\n\n"
        "Return the complete corrected ScreenPack as one JSON object. Fix every issue, keep everything else."
    )


def _latest[T: BaseModel](state: RunState, kind: str, schema: type[T]) -> T | None:
    """Latest artifact of `kind` (its .json file); falls back to the run state."""
    with open_session() as session:
        row = session.scalars(
            select(Artifact)
            .where(Artifact.run_id == state["run_id"], Artifact.type == kind, Artifact.path.like("%.json"))
            .order_by(Artifact.version.desc())
        ).first()
        path = row.path if row else None
    if path is not None:
        file = get_settings().runs_dir / path
        if file.is_file():
            return schema.model_validate_json(file.read_text(encoding="utf-8"))
    in_state = state.get(kind)  # type: ignore[misc]
    return schema.model_validate(in_state) if in_state else None


def persist_screenpack(run_id: str, pack: ScreenPack) -> int:
    with open_session() as session:
        latest = session.scalar(
            select(func.max(Artifact.version)).where(Artifact.run_id == run_id, Artifact.type == "screenpack")
        )
        version = (latest or 0) + 1
        run_dir = get_settings().runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        name = f"screenpack.v{version}.json"
        data = pack.model_dump_json(indent=2).encode("utf-8")
        (run_dir / name).write_bytes(data)
        session.add(
            Artifact(
                run_id=run_id, type="screenpack", version=version, path=f"{run_id}/{name}",
                sha256=hashlib.sha256(data).hexdigest(),
            )
        )  # fmt: skip
        session.commit()
    return version


async def run_screens(state: RunState) -> dict[str, Any]:
    run_id = state["run_id"]
    model = get_settings().default_smart_model
    async with step_scope(run_id, AGENT, model=model, reason=rerun_reason(state, AGENT)) as step_id:
        req = _latest(state, "requirements", Requirements)
        if req is None:
            raise ValueError("no requirements artifact to build screens from")
        arch = _latest(state, "architecture", Architecture)
        text = " ".join([req.title, req.summary, *(f.name for f in req.features)])
        kit = load_kit(sector_dir(req.sector, text))
        budget = node_budget(state)
        tokens_in = tokens_out = 0
        cost = 0.0
        user = build_prompt(req, arch, kit, revise_note(state, AGENT))
        pack: ScreenPack | None = None
        issues: list[Issue] = []
        for attempt in range(MAX_REPAIRS + 1):
            result = await complete_json(
                agent=AGENT, model=model, system=SYSTEM, user=user, schema=ScreenPack,
                max_tokens=MAX_TOKENS, run=budget, timeout=TIMEOUT_S, truncated_note=TRUNCATED_NOTE,
                reasoning_effort=REASONING_EFFORT,
            )  # fmt: skip
            tokens_in += result.tokens_in
            tokens_out += result.tokens_out
            cost += result.cost_usd
            pack = with_kit_css(result.value, kit)
            issues = validate(pack, kit)
            if not issues:
                break
            emit(run_id, AGENT, "log", message=f"screenpack attempt {attempt + 1}: {len(issues)} issues")
            user = repair_prompt(pack, issues, kit)
        with open_session() as session:
            row = session.get(AgentStep, step_id)
            if row is not None:
                row.tokens_in, row.tokens_out, row.cost_usd, row.model = tokens_in, tokens_out, cost, model
            run = session.get(Run, run_id)
            if run is not None:
                run.tokens_total += tokens_in + tokens_out
            session.commit()
        emit(
            run_id, AGENT, "cost", model=model, tokens_in=tokens_in, tokens_out=tokens_out, cost_usd=cost,
        )  # fmt: skip
        if issues or pack is None:
            raise ScreenPackInvalid(issues)
        version = persist_screenpack(run_id, pack)
        emit(run_id, AGENT, "log", message=f"screenpack v{version}: {len(pack.screens)} screens")
        return {
            "screenpack": pack.model_dump(mode="json"),
            "spent_delta": budget.charged_usd,
            **clear_note(state, AGENT),
        }


NODE = NodeSpec("screens", run_screens, "screens")
