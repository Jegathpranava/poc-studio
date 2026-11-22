"""Graph state (spec 7) plus the ScreenPack from 7b and a few routing fields. Every value is JSON-safe."""

import operator
from typing import Annotated, Any, Required, TypedDict


class RunState(TypedDict, total=False):
    run_id: Required[str]
    transcript_refs: list[str]  # paths relative to runs/<run_id>/
    requirements: dict[str, Any] | None
    architecture: dict[str, Any] | None
    screenpack: dict[str, Any] | None
    code_manifest: dict[str, Any] | None
    build_result: dict[str, Any] | None
    deck_result: dict[str, Any] | None  # {"ok": False, "error": ...} when pitch or assemble failed
    deck: dict[str, Any] | None
    video: dict[str, Any] | None
    qa_report: dict[str, Any] | None
    repo_url: str | None
    # Nodes return `spent_delta` (what they spent); parallel branches add up. Total spend = their sum.
    spent_delta: Annotated[float, operator.add]
    limit_usd: float
    # routing and gate bookkeeping
    gate1: dict[str, Any] | None  # last resume payload: {"decision", "edits", "note"}
    gate2: dict[str, Any] | None
    intelligence_note: str | None  # note from a Gate 1 "changes" decision
    revise_note: dict[str, str] | None  # Gate 2 "changes": {owning agent: note}; the agent clears it
    port_attempts: int | None  # a port retry's fresh build attempt budget (1..3); the port clears it
    free_polish: bool  # budget pause, "use the free model": the pitch keeps its titles unpolished
    qa_send_back: str | None  # "screens" | "pitch" | "port" | None; set by the QA agent
    sent_back_count: int
    block_publish: bool  # QA found a secret in the generated files: Gate 2 must not push
