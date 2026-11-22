"""Video (Pitch and Docs, third node): the approved deck HTML in, a walkthrough MP4 and `chapters.json` out.

Runs after Gate 2. A failed recording must not block publishing, but `step_scope` re-raises and the graph
would abort the run. Like `agents/port.py`, the failure is raised inside `step_scope` (the step ends `failed`
with an error event) and caught outside, and the node returns `{"video_result": {"ok": False, ...}}`.
`VIDEO_FAKE=1` swaps the browser for a 2 s clip, and is ignored when `APP_ENV=production`.
"""

import asyncio
import hashlib
import os
from pathlib import Path
from typing import Any

from sqlalchemy import select

from poc_studio.agents.store import next_version
from poc_studio.config import get_settings
from poc_studio.db.models import Artifact
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope
from poc_studio.media import video as media_video

AGENT = "video"
RESULT_KEY = "video_result"


class VideoFailed(RuntimeError):
    pass


def _latest_deck_html(run_id: str) -> Path | None:
    with open_session() as session:
        row = session.scalars(
            select(Artifact)
            .where(Artifact.run_id == run_id, Artifact.type == "deck", Artifact.path.like("%.html"))
            .order_by(Artifact.version.desc())
        ).first()
        path = row.path if row else None
    return get_settings().runs_dir / path if path else None


def _add_artifact(run_id: str, version: int, file: Path) -> None:
    rel = file.relative_to(get_settings().runs_dir).as_posix()
    with open_session() as session:
        session.add(
            Artifact(
                run_id=run_id, type="video", version=version, path=rel,
                sha256=hashlib.sha256(file.read_bytes()).hexdigest(),
            )
        )  # fmt: skip
        session.commit()


def _fake_enabled() -> bool:
    return os.environ.get("VIDEO_FAKE") == "1" and get_settings().app_env != "production"


async def _record(run_id: str, deck: Path) -> dict[str, Any]:
    version = next_version(run_id, "video")
    out = deck.with_name(f"{deck.name.split('.v')[0]}.v{version}.mp4")
    fake = _fake_enabled()
    if fake:
        emit(run_id, AGENT, "log", status="warning", message="Video is a placeholder clip: VIDEO_FAKE is on")
    recorder = media_video.fake_record if fake else media_video.record
    try:
        result = await asyncio.to_thread(recorder, deck, out)
    except media_video.VideoError as exc:
        raise VideoFailed(str(exc)) from exc
    _add_artifact(run_id, version, result.path)
    chapters = result.path.with_suffix(
        ".chapters.json"
    )  # versioned like the MP4; the recorder writes plain chapters.json
    (result.path.parent / "chapters.json").replace(chapters)
    _add_artifact(run_id, version, chapters)
    check = media_video.video_check(result)
    emit(
        run_id,
        AGENT,
        "log",
        message=f"video v{version}: {result.duration_s:.0f} s, {len(result.chapters)} chapters",
    )
    return {
        "ok": True, "path": f"{run_id}/deck/{out.name}", "duration_s": result.duration_s,
        "chapters": [c.model_dump() for c in result.chapters], "check": check,
    }  # fmt: skip


async def run_video(state: RunState) -> dict[str, Any]:
    run_id = state["run_id"]
    try:
        async with step_scope(run_id, AGENT) as _:
            deck = _latest_deck_html(run_id)
            if deck is None or not deck.is_file():  # assemble was stubbed or skipped
                emit(run_id, AGENT, "log", message="video skipped, no deck html")
                skipped = {"ok": False, "skipped": True}
                return {RESULT_KEY: skipped, "video": skipped}
            outcome = await _record(run_id, deck)
    except VideoFailed as exc:  # the step is already `failed`; publishing goes on
        failed = {"ok": False, "error": {"message": str(exc)[:500]}}
        return {RESULT_KEY: failed, "video": failed}
    return {RESULT_KEY: outcome, "video": outcome}


NODE = NodeSpec("video", run_video, "video")
