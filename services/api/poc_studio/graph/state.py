"""Graph state (spec 7) plus the ScreenPack from 7b and a few routing fields. Every value is JSON-safe."""

from typing import Annotated, Any, Required, TypedDict


def last_write_wins(old: dict[str, Any] | None, new: dict[str, Any] | None) -> dict[str, Any] | None:
    """Parallel branches (pitch, port) may both return `budget`; the later write wins."""
    return new if new is not None else old


class RunState(TypedDict, total=False):
    run_id: Required[str]
    transcript_refs: list[str]  # paths relative to runs/<run_id>/
    requirements: dict[str, Any] | None
    architecture: dict[str, Any] | None
    screenpack: dict[str, Any] | None
    code_manifest: dict[str, Any] | None
    build_result: dict[str, Any] | None
    deck: dict[str, Any] | None
    video: dict[str, Any] | None
    qa_report: dict[str, Any] | None
    repo_url: str | None
    budget: Annotated[dict[str, Any] | None, last_write_wins]  # {"limit_usd": float, "spent_usd": float}
    # routing and gate bookkeeping
    gate1: dict[str, Any] | None  # last resume payload: {"decision", "edits", "note"}
    gate2: dict[str, Any] | None
    intelligence_note: str | None  # note from a Gate 1 "changes" decision
    qa_send_back: str | None  # "screens" | "pitch" | "port" | None; set by the QA agent
    sent_back_count: int
