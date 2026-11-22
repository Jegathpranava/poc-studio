"""QA Reviewer (agent 6): runs the spec 7a/7b checks, writes `qa_report.v<N>.json` and routes the send-back.

State it sets for the graph: `qa_send_back` ("pitch" | "screens" | "port" | None, read by `after_qa`),
`sent_back_count` (send-backs carried out so far; one this node asks for counts at the next QA run, because
`after_qa` reads the count straight after this node and stops at MAX_SEND_BACKS), `block_publish` (a secret
was found; Gate 2 and the publish step must not push) and `qa_report`. A failing QA never stops the run: it
reports and the run goes on to Gate 2, with `deck_present` marked failed when there is no deck.
"""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ValidationError
from sqlalchemy import select

from poc_studio.agents.store import latest_json, next_version, record, stub_skip_allowed
from poc_studio.config import get_settings
from poc_studio.db.models import Artifact
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope
from poc_studio.qa.checks import QAInputs, run_checks
from poc_studio.qa.routing import decide
from poc_studio.qa.secrets import Finding, scan_tree
from poc_studio.schemas.architecture import Architecture
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.requirements import Requirements
from poc_studio.schemas.screenpack import ScreenPack

AGENT = "qa"
SCAN_ROOTS = ("app", "deck", "docs")


def _load[T: BaseModel](state: RunState, kind: str, schema: type[T]) -> T | None:
    try:
        return latest_json(state, kind, schema)
    except (ValidationError, ValueError):
        return None  # an unreadable artifact counts as missing


def _deck_html(run_id: str) -> str | None:
    with open_session() as session:
        row = session.scalars(
            select(Artifact)
            .where(Artifact.run_id == run_id, Artifact.type == "deck", Artifact.path.like("%.html"))
            .order_by(Artifact.version.desc())
        ).first()
        path = row.path if row else None
    file = get_settings().runs_dir / path if path else None
    return file.read_text(encoding="utf-8") if file is not None and file.is_file() else None


def _build_info(state: RunState, run_dir: Path) -> dict[str, Any] | None:
    result = state.get("build_result")
    if result is not None:
        return result
    file = run_dir / "build.json"
    return json.loads(file.read_text(encoding="utf-8")) if file.is_file() else None


def _readme(run_dir: Path) -> str:
    for rel in ("app/README.md", "README.md"):
        file = run_dir / rel
        if file.is_file():
            return file.read_text(encoding="utf-8", errors="replace")
    return ""


def _scan(run_dir: Path, names: list[str]) -> tuple[list[Finding], list[Finding]]:
    secrets: list[Finding] = []
    pii: list[Finding] = []
    for root in SCAN_ROOTS:
        base = run_dir / root
        secrets += [f.model_copy(update={"file": f"{root}/{f.file}"}) for f in scan_tree(base)]
        pii += [
            f.model_copy(update={"file": f"{root}/{f.file}"})
            for f in scan_tree(base, pii=True, allow_names=names)
            if f.kind in ("email", "phone")
        ]
    return secrets, pii


def gather(state: RunState) -> QAInputs:
    run_id = state["run_id"]
    run_dir = get_settings().runs_dir / run_id
    req = _load(state, "requirements", Requirements)
    names = [s.name for s in req.stakeholders] if req else []
    secrets, pii = _scan(run_dir, names)
    deck_result = state.get("deck_result") or {}
    return QAInputs(
        req=req,
        arch=_load(state, "architecture", Architecture),
        pack=_load(state, "screenpack", ScreenPack),
        plan=_load(state, "deck", DeckPlan),
        deck_html=_deck_html(run_id),
        deck_failed=deck_result.get("ok") is False,
        build=_build_info(state, run_dir),
        readme=_readme(run_dir),
        secret_findings=secrets,
        pii_findings=pii,
        lenient=stub_skip_allowed(),
    )


async def run_qa(state: RunState) -> dict[str, Any]:
    run_id = state["run_id"]
    async with step_scope(run_id, AGENT):
        checks = run_checks(gather(state))
        # `after_qa` stops at MAX_SEND_BACKS right after this node, so the count is of send-backs already
        # carried out. A `qa_send_back` still in state from the last QA run was executed: count it now.
        sent_back = state.get("sent_back_count", 0) + (1 if state.get("qa_send_back") else 0)
        decision = decide(checks, sent_back)
        for c in checks:
            if not c.ok:
                emit(run_id, AGENT, "log", message=f"QA failed {c.name} ({c.owner_agent}): {c.detail}")
        report = {
            "checks": [c.model_dump() for c in checks],
            "passed": [c.name for c in checks if c.ok],
            "failed": [c.name for c in checks if not c.ok],
            "send_back": decision["send_back"],
            "block_publish": decision["block_publish"],
            "sent_back_count": sent_back,
        }
        version = next_version(run_id, "qa_report")
        body = json.dumps(report, indent=2).encode()
        record(run_id, "qa_report", version, f"qa_report.v{version}.json", body)
        emit(
            run_id, AGENT, "log",
            message=f"qa report v{version}: {len(report['failed'])} failed, back to {decision['send_back']}",
        )  # fmt: skip
        return {
            "qa_report": report,
            "qa_send_back": decision["send_back"],
            "sent_back_count": sent_back,
            "block_publish": decision["block_publish"],
        }


NODE = NodeSpec("qa", run_qa, "qa")
