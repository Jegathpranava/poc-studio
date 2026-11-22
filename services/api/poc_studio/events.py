"""In-process event bus. Every event is persisted to `events` (redacted) and fanned out to subscribers.

Subscribers own an asyncio queue bound to their own loop, and `emit` may be called from any thread.
"""

import asyncio
import json
import threading
from dataclasses import dataclass
from datetime import UTC
from typing import Any

from sqlalchemy import select

from poc_studio.db.models import Event, now
from poc_studio.db.session import open_session
from poc_studio.redact import redact, redact_obj
from poc_studio.routes.schemas import RunEvent

KINDS = ("status", "log", "cost", "gate", "error")
RUN_AGENT = "run"  # events about the run itself, not one agent


def event_name(ev: RunEvent) -> str:
    """The SSE event name: `run` for run-level events, `step` for per-agent ones."""
    return "run" if ev.agent == RUN_AGENT or ev.kind == "gate" else "step"


def to_event(row: Event) -> RunEvent:
    ts = row.ts if row.ts.tzinfo else row.ts.replace(tzinfo=UTC)  # SQLite drops the zone on read
    extra: dict[str, Any] = json.loads(row.data) if row.data else {}
    return RunEvent.model_validate(
        {
            "id": row.id,
            "ts": ts,
            "run_id": row.run_id,
            "agent": row.agent,
            "kind": row.level,
            "message": row.message or None,
            **extra,
        }
    )


def load_events(run_id: str, after_id: int = 0) -> list[RunEvent]:
    with open_session() as session:
        rows = session.scalars(
            select(Event).where(Event.run_id == run_id, Event.id > after_id).order_by(Event.id)
        ).all()
        return [to_event(r) for r in rows]


@dataclass(eq=False)
class Subscription:
    loop: asyncio.AbstractEventLoop
    queue: "asyncio.Queue[RunEvent]"


class EventBus:
    def __init__(self) -> None:
        self._subs: dict[str, set[Subscription]] = {}
        self._lock = threading.Lock()

    def subscribe(self, run_id: str) -> Subscription:
        """Call from the loop that will read the queue (the API's loop)."""
        sub = Subscription(asyncio.get_running_loop(), asyncio.Queue())
        with self._lock:
            self._subs.setdefault(run_id, set()).add(sub)
        return sub

    def unsubscribe(self, run_id: str, sub: Subscription) -> None:
        with self._lock:
            subs = self._subs.get(run_id)
            if subs:
                subs.discard(sub)
                if not subs:
                    del self._subs[run_id]

    def publish(self, ev: RunEvent) -> None:
        with self._lock:
            subs = list(self._subs.get(ev.run_id, ()))
        for sub in subs:
            try:
                sub.loop.call_soon_threadsafe(sub.queue.put_nowait, ev)
            except RuntimeError:  # that loop is closed
                self.unsubscribe(ev.run_id, sub)

    def emit(self, run_id: str, agent: str, kind: str, **fields: Any) -> RunEvent:
        """Persist the event (redacted) and fan it out. `message` is the text; the rest is spec 7b data."""
        if kind not in KINDS:
            raise ValueError(f"unknown event kind {kind!r}")
        message = redact(str(fields.pop("message", "") or ""))
        extra = {k: redact_obj(v) for k, v in fields.items() if v is not None}
        with open_session() as session:
            row = Event(
                run_id=run_id,
                ts=now(),
                agent=agent,
                level=kind,
                message=message,
                data=json.dumps(extra, default=str) if extra else None,
            )
            session.add(row)
            session.commit()
            ev = to_event(row)
        self.publish(ev)
        return ev


bus = EventBus()


def emit(run_id: str, agent: str, kind: str, **fields: Any) -> RunEvent:
    return bus.emit(run_id, agent, kind, **fields)
