"""GET /api/runs/{id}/events: SSE with replay from Last-Event-ID, then live."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sse_starlette import EventSourceResponse, ServerSentEvent

from poc_studio.db.models import Run
from poc_studio.db.session import get_session
from poc_studio.events import bus, event_name, load_events
from poc_studio.routes.schemas import RunEvent

router = APIRouter()


def _sse(ev: RunEvent) -> ServerSentEvent:
    return ServerSentEvent(data=ev.model_dump_json(exclude_none=True), event=event_name(ev), id=str(ev.id))


async def event_stream(run_id: str, after_id: int, follow: bool) -> AsyncIterator[ServerSentEvent]:
    sub = bus.subscribe(run_id)  # subscribe before replaying, so nothing falls in the gap
    try:
        last = after_id
        for ev in load_events(run_id, after_id):
            last = ev.id
            yield _sse(ev)
        if not follow:
            return
        while True:
            ev = await sub.queue.get()
            if ev.id > last:  # drop what the replay already sent
                last = ev.id
                yield _sse(ev)
    finally:
        bus.unsubscribe(run_id, sub)


@router.get("/runs/{run_id}/events")
async def stream_events(
    run_id: str,
    session: Session = Depends(get_session),
    last_event_id: Annotated[str | None, Header(alias="Last-Event-ID")] = None,
    follow: bool = True,
) -> EventSourceResponse:
    """`follow=false` ends the stream after the replay (for tests and curl)."""
    if session.get(Run, run_id) is None:
        raise HTTPException(404, f"run {run_id} not found")
    try:
        after = max(int(last_event_id), 0) if last_event_id else 0
    except ValueError:
        after = 0
    return EventSourceResponse(event_stream(run_id, after, follow), ping=15)
