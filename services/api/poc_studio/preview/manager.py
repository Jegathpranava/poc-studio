"""Preview servers: `next start` for a built prototype, on a free port in 4300 to 4399.

The UI iframes the server directly (`http://127.0.0.1:<port>/`), so no proxy is involved and `touch` is called
each time the UI asks for the preview (the page re-asks every few minutes while it is open). A server idle for
more than 30 minutes is stopped by the reaper. Pids and ports are stored in `runs` so a restarted API can kill
the orphans (`kill_orphans`).
"""

import asyncio
import contextlib
import shutil
import socket
import time
from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from pathlib import Path

import httpx
from sqlalchemy import select

from poc_studio.config import get_settings
from poc_studio.db.models import Run
from poc_studio.db.session import open_session
from poc_studio.sandbox.procs import (
    IS_WINDOWS,
    kill_pid_tree,
    looks_like_preview_image,
    pid_alive,
    process_image,
)
from poc_studio.sandbox.runner import child_env

PORT_RANGE = range(4300, 4400)
IDLE_S = 30 * 60
START_TIMEOUT_S = 30.0
HOST = "127.0.0.1"


class PreviewError(RuntimeError):
    """The preview server could not be started."""


@dataclass
class Entry:
    pid: int
    port: int
    last_used: float


Launcher = Callable[[Path, int], Awaitable[int]]
ReadyCheck = Callable[[int, int, float], Awaitable[bool]]


def port_is_free(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind((HOST, port))
        except OSError:
            return False
    return True


async def launch_next(app_dir: Path, port: int) -> int:
    """Start `npm run start -- -p <port> -H 127.0.0.1` with the allow-listed env. Returns the pid."""
    npm = shutil.which("npm", path=child_env().get("PATH")) or "npm"
    proc = await asyncio.create_subprocess_exec(
        npm, "run", "start", "--", "-p", str(port), "-H", HOST,
        cwd=app_dir, env=child_env(app_dir.resolve().parent / ".home"),
        stdin=asyncio.subprocess.DEVNULL, stdout=asyncio.subprocess.DEVNULL,
        stderr=asyncio.subprocess.DEVNULL,
        start_new_session=not IS_WINDOWS,
    )  # fmt: skip
    return proc.pid


async def http_ready(port: int, pid: int, timeout_s: float) -> bool:
    """Poll until the server answers HTTP, the process dies or the timeout passes."""
    deadline = time.monotonic() + timeout_s
    async with httpx.AsyncClient(timeout=2.0) as client:
        while time.monotonic() < deadline:
            try:
                await client.get(f"http://{HOST}:{port}/")
                return True
            except httpx.HTTPError:
                pass
            if not await asyncio.to_thread(pid_alive, pid):
                return False
            await asyncio.sleep(0.25)
    return False


class PreviewManager:
    def __init__(
        self,
        *,
        launcher: Launcher = launch_next,
        ready: ReadyCheck = http_ready,
        kill: Callable[[int], None] = kill_pid_tree,
        alive: Callable[[int], bool] = pid_alive,
        port_free: Callable[[int], bool] = port_is_free,
        image: Callable[[int], str] = process_image,
        clock: Callable[[], float] = time.monotonic,
        idle_s: float = IDLE_S,
        start_timeout_s: float = START_TIMEOUT_S,
    ) -> None:
        self._launcher, self._ready, self._kill, self._alive = launcher, ready, kill, alive
        self._port_free, self._clock, self._image = port_free, clock, image
        self._alloc_lock = asyncio.Lock()  # one port is picked at a time ...
        self._reserved: set[int] = set()  # ... and held here from the pick until the server is live or failed
        self.idle_s, self.start_timeout_s = idle_s, start_timeout_s
        self._live: dict[str, Entry] = {}
        self._locks: dict[str, asyncio.Lock] = {}
        self._reaper: asyncio.Task[None] | None = None

    # -- state in `runs` -------------------------------------------------------------------------
    @staticmethod
    def _record(run_id: str, pid: int | None, port: int | None) -> None:
        with open_session() as session:
            run = session.get(Run, run_id)
            if run is not None:
                run.preview_pid, run.preview_port = pid, port
                session.commit()

    async def _pick_port(self) -> int:
        """Pick a free port and reserve it under the manager-wide lock, so concurrent runs never share one."""
        async with self._alloc_lock:
            taken = {e.port for e in self._live.values()} | self._reserved
            for port in PORT_RANGE:
                if port not in taken and self._port_free(port):
                    self._reserved.add(port)
                    return port
        raise PreviewError("No free preview port in 4300 to 4399")

    # -- public API ------------------------------------------------------------------------------
    def port_of(self, run_id: str) -> int | None:
        entry = self._live.get(run_id)
        return entry.port if entry else None

    def touch(self, run_id: str) -> None:
        entry = self._live.get(run_id)
        if entry is not None:
            entry.last_used = self._clock()

    async def ensure(self, run_id: str) -> int:
        """The port of a live server for the run, starting one when needed. Raises `PreviewError`."""
        lock = self._locks.setdefault(run_id, asyncio.Lock())
        async with lock:
            entry = self._live.get(run_id)
            if entry is not None:
                if await asyncio.to_thread(self._alive, entry.pid):
                    entry.last_used = self._clock()
                    return entry.port
                self._forget(run_id)
            app_dir = get_settings().runs_dir / run_id / "app"
            if not app_dir.is_dir():
                raise PreviewError("The prototype app folder is missing")
            port = await self._pick_port()
            try:
                return await self._start(run_id, app_dir, port)
            finally:
                self._reserved.discard(port)  # live now (tracked in _live) or failed

    async def _start(self, run_id: str, app_dir: Path, port: int) -> int:
        try:
            pid = await self._launcher(app_dir, port)
        except OSError as exc:
            raise PreviewError(f"Could not start the preview server: {exc}") from exc
        if not await self._ready(port, pid, self.start_timeout_s):
            await asyncio.to_thread(self._kill, pid)
            raise PreviewError("The preview server did not answer within 30 seconds")
        if not await asyncio.to_thread(self._alive, pid):  # something else may have answered on the port
            await asyncio.to_thread(self._kill, pid)
            raise PreviewError("The preview server exited right after it started")
        self._live[run_id] = Entry(pid, port, self._clock())
        self._record(run_id, pid, port)
        return port

    def _forget(self, run_id: str) -> None:
        self._live.pop(run_id, None)
        self._record(run_id, None, None)

    async def stop(self, run_id: str) -> None:
        entry = self._live.get(run_id)
        lock = self._locks.get(run_id)
        if lock is not None and not lock.locked():
            del self._locks[run_id]  # keep the lock table bounded
        if entry is None:
            return
        await asyncio.to_thread(self._kill, entry.pid)
        self._forget(run_id)

    async def stop_all(self) -> None:
        if self._reaper is not None:
            self._reaper.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._reaper
            self._reaper = None
        for run_id in list(self._live):
            await self.stop(run_id)

    async def reap_idle(self) -> list[str]:
        """Stop servers idle for more than `idle_s`. Returns the run ids stopped."""
        now = self._clock()
        stale = [rid for rid, e in self._live.items() if now - e.last_used > self.idle_s]
        for run_id in stale:
            await self.stop(run_id)
        return stale

    def start_reaper(self, interval_s: float = 60.0) -> None:
        async def loop() -> None:
            while True:
                await asyncio.sleep(interval_s)
                await self.reap_idle()

        if self._reaper is None:
            self._reaper = asyncio.create_task(loop())

    async def kill_orphans(self) -> list[int]:
        """On API start: kill recorded preview servers, then clear pid and port.

        A pid is killed only when it is alive, its image is node or cmd (next) AND the recorded port still
        listens; otherwise the pid was reused by an unrelated process and only the record is cleared.
        """
        with open_session() as session:
            rows = session.execute(
                select(Run.id, Run.preview_pid, Run.preview_port).where(Run.preview_pid.is_not(None))
            ).all()
        killed: list[int] = []
        for run_id, pid, port in rows:
            if pid is not None and await asyncio.to_thread(self._is_ours, pid, port):
                await asyncio.to_thread(self._kill, pid)
                killed.append(pid)
            self._record(run_id, None, None)
        return killed

    def _is_ours(self, pid: int, port: int | None) -> bool:
        if not self._alive(pid) or not looks_like_preview_image(self._image(pid)):
            return False
        return port is not None and not self._port_free(port)  # a listening port cannot be bound again
