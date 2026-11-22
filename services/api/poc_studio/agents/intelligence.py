"""Meeting Intelligence (agent 1): transcript in, validated `requirements` artifact out."""

import hashlib
import re
from typing import Any

from sqlalchemy import func, select

from poc_studio.config import get_settings
from poc_studio.db.models import AgentStep, Artifact, Project, Run
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope
from poc_studio.ingest import Transcript, parse_files
from poc_studio.llm import RunBudget, complete_json, wrap_untrusted
from poc_studio.schemas.requirements import Requirements

AGENT = "intelligence"
MAX_TOKENS = 4000

SYSTEM = (
    "You are the Meeting Intelligence agent. Read the meeting transcript and extract a scoped brief "
    "for an AI proof of concept.\n\nRules:\n"
    "- Every feature needs a `source_quote`: an exact, verbatim excerpt from the transcript (no "
    "paraphrase), and `source_ts` taken from the segment timestamp when known.\n"
    "- Rank features P1 (must have), P2, P3. Set `confidence` from 0 to 1.\n"
    "- A constraint is `confirmed` only when the client stated it plainly; give its verbatim "
    "`source_quote`.\n"
    "- `sector` is one of logistics, healthcare, e-commerce, fintech, or other.\n"
    "- `summary` is 2 to 5 sentences. `title` is a short use-case title.\n"
    "- Use null for anything the transcript does not say. Never invent facts."
)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def format_ts(ts: float | None) -> str:
    if ts is None:
        return "--:--:--"
    s = int(ts)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def render_transcript(transcript: Transcript) -> str:
    lines = []
    for seg in transcript.segments:
        who = f" {seg.speaker}:" if seg.speaker else ""
        lines.append(f"[{format_ts(seg.ts)}]{who} {seg.text}")
    return "\n".join(lines)


def build_prompt(client: str, transcript: Transcript, note: str | None) -> str:
    parts = [
        f"Client: {client}",
        "Transcript, one segment per line as [hh:mm:ss] speaker: text:",
        wrap_untrusted(render_transcript(transcript)),
    ]
    if note:
        parts.append(
            f"The owner reviewed an earlier extraction and asks for these changes. Apply them:\n{note}"
        )
    return "\n\n".join(parts)


def validate_against_transcript(req: Requirements, transcript: Transcript) -> tuple[Requirements, list[str]]:
    """Drop features whose quote is not in the text; unconfirm constraints without a found quote."""
    haystack = _norm(" ".join(s.text for s in transcript.segments))

    def found(quote: str | None) -> bool:
        return bool(quote and _norm(quote) and _norm(quote) in haystack)

    warnings: list[str] = []
    kept = []
    for feature in req.features:
        if found(feature.source_quote):
            kept.append(feature)
        else:
            warnings.append(f"Dropped feature {feature.name!r}: its source quote is not in the transcript")
    constraints = [
        c.model_copy(update={"confirmed": c.confirmed and found(c.source_quote)}) for c in req.constraints
    ]
    return req.model_copy(update={"features": kept, "constraints": constraints}), warnings


def load_transcript(state: RunState) -> Transcript:
    run_dir = get_settings().runs_dir / state["run_id"]
    refs = state.get("transcript_refs")
    if refs:
        files = [run_dir / r for r in refs]
    else:
        files = sorted(p for p in (run_dir / "input").iterdir() if p.is_file())
    return parse_files(files)


def _next_version(run_id: str) -> int:
    with open_session() as session:
        latest = session.scalar(
            select(func.max(Artifact.version)).where(
                Artifact.run_id == run_id, Artifact.type == "requirements"
            )
        )
    return (latest or 0) + 1


def _persist(run_id: str, version: int, req: Requirements) -> None:
    path = get_settings().runs_dir / run_id / f"requirements.v{version}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    data = req.model_dump_json(indent=2).encode("utf-8")
    path.write_bytes(data)
    with open_session() as session:
        session.add(
            Artifact(
                run_id=run_id,
                type="requirements",
                version=version,
                path=f"{run_id}/{path.name}",
                sha256=hashlib.sha256(data).hexdigest(),
            )
        )
        run = session.get(Run, run_id)
        if run is not None:
            run.title = req.title[:300]
            project = session.get(Project, run.project_id)
            if project is not None and not project.sector:
                project.sector = req.sector
        session.commit()


def _client_name(run_id: str) -> str:
    with open_session() as session:
        run = session.get(Run, run_id)
        project = session.get(Project, run.project_id) if run else None
        return project.client_name if project else ""


def _record_usage(
    step_id: int, run_id: str, tokens_in: int, tokens_out: int, cost: float, model: str
) -> None:
    with open_session() as session:
        row = session.get(AgentStep, step_id)
        if row is not None:
            row.tokens_in, row.tokens_out, row.cost_usd, row.model = tokens_in, tokens_out, cost, model
        run = session.get(Run, run_id)
        if run is not None:
            run.paid_usd += cost
            run.tokens_total += tokens_in + tokens_out
        session.commit()


async def run_intelligence(state: RunState) -> dict[str, Any]:
    run_id = state["run_id"]
    settings = get_settings()
    model = settings.default_fast_model
    async with step_scope(run_id, AGENT, model=model) as step_id:
        transcript = load_transcript(state)
        b = state.get("budget") or {}
        budget = RunBudget(run_id, b.get("limit_usd", settings.run_budget_usd), b.get("spent_usd", 0.0))
        result = await complete_json(
            agent=AGENT,
            model=model,
            system=SYSTEM,
            user=build_prompt(_client_name(run_id), transcript, state.get("intelligence_note")),
            schema=Requirements,
            max_tokens=MAX_TOKENS,
            run=budget,
        )
        _record_usage(step_id, run_id, result.tokens_in, result.tokens_out, result.cost_usd, result.model)
        emit(
            run_id, AGENT, "cost", model=result.model, tokens_in=result.tokens_in,
            tokens_out=result.tokens_out, cost_usd=result.cost_usd,
        )  # fmt: skip
        req, warnings = validate_against_transcript(result.value, transcript)
        for warning in warnings:
            emit(run_id, AGENT, "log", status="warning", message=warning)
        if not req.features:
            raise ValueError("no feature has a source quote found in the transcript")
        version = _next_version(run_id)
        _persist(run_id, version, req)
        emit(run_id, AGENT, "log", message=f"requirements v{version}: {len(req.features)} features")
        return {
            "requirements": req.model_dump(mode="json"),
            "budget": {"limit_usd": budget.limit_usd, "spent_usd": budget.spent_usd},
            "intelligence_note": None,
        }


NODE = NodeSpec("intelligence", run_intelligence, "intelligence")
