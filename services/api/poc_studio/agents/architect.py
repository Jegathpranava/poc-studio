"""Solution Architect (agent 2): approved requirements in, `architecture` artifact (JSON and Markdown) out."""

import hashlib
import json
from typing import Any

from sqlalchemy import func, select

from poc_studio.config import get_settings
from poc_studio.db.models import AgentStep, Artifact, Run
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.spend import node_budget
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope
from poc_studio.llm import complete_json, wrap_untrusted
from poc_studio.schemas.architecture import Architecture
from poc_studio.schemas.requirements import Requirements

AGENT = "architect"
MAX_TOKENS = 6000

SYSTEM = (
    "You are the Solution Architect agent. From an approved requirements brief, design a small AI "
    "proof-of-concept system.\n\nRules:\n"
    "- `use_case_class` is one of rag, agent, classifier, vision, forecasting, other.\n"
    "- `components`: 3 to 12 parts, each with a name, a kind (ingest, service, llm, api, ui, store, ...) "
    "and one sentence of detail.\n"
    "- `mermaid` is one flowchart that starts with `flowchart` or `graph`; use plain node labels.\n"
    "- `models`: 1 to 8 picks, each with the job, the model and the cost per 1k calls in USD. Prefer the "
    "free `fast` and `smart` models; use `claude-haiku-5-5` only for executive polish.\n"
    "- `monthly_cost.lines` list each cost item in USD; `total_usd` must equal their sum. State the "
    "assumptions.\n"
    "- `phases`: build phases with their length in weeks. Fit the stated budget and timeline.\n"
    "- Do not rely on constraints marked unconfirmed. Never invent facts the brief does not support.\n"
    "- `rationale` is a short paragraph on why this design fits the brief."
)


def build_prompt(req: Requirements) -> str:
    # The brief is not raw transcript, but it quotes transcript text, so it is passed as data.
    return "Approved requirements brief (JSON):\n\n" + wrap_untrusted(
        json.dumps(req.model_dump(mode="json"), indent=2)
    )


def render_markdown(title: str, arch: Architecture) -> str:
    out = [f"# Architecture: {title}", "", f"Use case class: `{arch.use_case_class}`", ""]
    out += ["## Approach", "", arch.rationale, "", "## System diagram", ""]
    out += ["```mermaid", arch.mermaid.strip(), "```", "", "## Components", ""]
    out += [f"- **{c.name}** ({c.kind}): {c.detail}" for c in arch.components]
    out += ["", "## Model picks", "", "| Job | Model | Cost per 1k calls (USD) |", "| --- | --- | ---: |"]
    out += [f"| {m.job} | `{m.model}` | {m.cost_per_1k_calls_usd:.2f} |" for m in arch.models]
    out += ["", "## Monthly cost", "", "| Item | USD |", "| --- | ---: |"]
    out += [f"| {ln.item} | {ln.usd:.2f} |" for ln in arch.monthly_cost.lines]
    out += [f"| **Total** | **{arch.monthly_cost.total_usd:.2f}** |", "", arch.monthly_cost.assumptions]
    if arch.phases:
        out += ["", "## Phases", ""]
        out += [f"{i}. **{p.name}** ({p.weeks:g} wk): {p.detail}" for i, p in enumerate(arch.phases, 1)]
    return "\n".join(out) + "\n"


def _latest_requirements(state: RunState) -> Requirements:
    """The approved brief: the latest `requirements` artifact (Gate 1 edits are saved as a new version)."""
    run_id = state["run_id"]
    with open_session() as session:
        row = session.scalars(
            select(Artifact)
            .where(Artifact.run_id == run_id, Artifact.type == "requirements")
            .order_by(Artifact.version.desc())
        ).first()
        path = row.path if row else None
    if path is not None:
        file = get_settings().runs_dir / path
        if file.is_file():
            return Requirements.model_validate_json(file.read_text(encoding="utf-8"))
    in_state = state.get("requirements")
    if in_state:
        return Requirements.model_validate(in_state)
    raise ValueError("no requirements artifact to design from")


def persist_architecture(run_id: str, title: str, arch: Architecture) -> int:
    with open_session() as session:
        latest = session.scalar(
            select(func.max(Artifact.version)).where(
                Artifact.run_id == run_id, Artifact.type == "architecture"
            )
        )
        version = (latest or 0) + 1
        run_dir = get_settings().runs_dir / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        files = {
            f"architecture.v{version}.json": arch.model_dump_json(indent=2).encode("utf-8"),
            f"architecture.v{version}.md": render_markdown(title, arch).encode("utf-8"),
        }
        for name, data in files.items():
            (run_dir / name).write_bytes(data)
            session.add(
                Artifact(
                    run_id=run_id,
                    type="architecture",
                    version=version,
                    path=f"{run_id}/{name}",
                    sha256=hashlib.sha256(data).hexdigest(),
                )
            )
        session.commit()
    return version


async def run_architect(state: RunState) -> dict[str, Any]:
    run_id = state["run_id"]
    model = get_settings().default_smart_model
    async with step_scope(run_id, AGENT, model=model) as step_id:
        req = _latest_requirements(state)
        budget = node_budget(state)
        result = await complete_json(
            agent=AGENT, model=model, system=SYSTEM, user=build_prompt(req), schema=Architecture,
            max_tokens=MAX_TOKENS, run=budget,
        )  # fmt: skip
        with open_session() as session:
            row = session.get(AgentStep, step_id)
            if row is not None:
                row.tokens_in, row.tokens_out = result.tokens_in, result.tokens_out
                row.cost_usd, row.model = result.cost_usd, result.model
            run = session.get(Run, run_id)
            if run is not None:
                run.tokens_total += result.tokens_in + result.tokens_out
            session.commit()
        emit(
            run_id, AGENT, "cost", model=result.model, tokens_in=result.tokens_in,
            tokens_out=result.tokens_out, cost_usd=result.cost_usd,
        )  # fmt: skip
        version = persist_architecture(run_id, req.title, result.value)
        count = len(result.value.components)
        emit(run_id, AGENT, "log", message=f"architecture v{version}: {count} components")
        return {"architecture": result.value.model_dump(mode="json"), "spent_delta": budget.charged_usd}


NODE = NodeSpec("architect", run_architect, "architect")
