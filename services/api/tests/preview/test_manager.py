import asyncio
from pathlib import Path

import pytest

from poc_studio.config import get_settings
from poc_studio.db.models import Project, Run
from poc_studio.db.session import open_session
from poc_studio.preview.manager import PORT_RANGE, PreviewError, PreviewManager
from poc_studio.sandbox.procs import IS_WINDOWS


class Fake:
    """A fake process launcher, kill function and clock."""

    def __init__(self) -> None:
        self.launched: list[tuple[Path, int]] = []
        self.killed: list[int] = []
        self.alive_pids: set[int] = set()
        self.now = 0.0
        self.ready_ok = True
        self.images: dict[int, str] = {}
        self.launch_delay = 0.0
        self._pid = 1000

    async def launcher(self, app_dir: Path, port: int) -> int:
        self._pid += 1
        pid = self._pid
        if self.launch_delay:
            await asyncio.sleep(self.launch_delay)
        self.launched.append((app_dir, port))
        self.alive_pids.add(pid)
        return pid

    async def ready(self, port: int, pid: int, timeout_s: float) -> bool:
        return self.ready_ok

    def kill(self, pid: int) -> None:
        self.killed.append(pid)
        self.alive_pids.discard(pid)

    def manager(self, busy: set[int] | None = None) -> PreviewManager:
        return PreviewManager(
            launcher=self.launcher,
            ready=self.ready,
            kill=self.kill,
            alive=lambda p: p in self.alive_pids,
            port_free=lambda p: p not in (busy or set()),
            image=lambda p: self.images.get(p, ""),
            clock=lambda: self.now,
        )


def make_runs(env: Path, *run_ids: str) -> None:
    with open_session() as session:
        project = Project(client_name="Acme", client_name_key="acme")
        session.add(project)
        session.flush()
        for rid in run_ids:
            session.add(Run(id=rid, project_id=project.id, title="t"))
            (get_settings().runs_dir / rid / "app").mkdir(parents=True)
        session.commit()


def recorded(run_id: str) -> tuple[int | None, int | None]:
    with open_session() as session:
        run = session.get(Run, run_id)
        assert run is not None
        return run.preview_pid, run.preview_port


async def test_port_in_range_reused_per_run_and_distinct_across_runs(env: Path) -> None:
    make_runs(env, "r_aaaaaa", "r_bbbbbb")
    fake = Fake()
    mgr = fake.manager(busy={4300})
    first = await mgr.ensure("r_aaaaaa")
    assert first in PORT_RANGE and first == 4301  # 4300 is busy, so it is skipped
    assert await mgr.ensure("r_aaaaaa") == first
    assert len(fake.launched) == 1
    assert recorded("r_aaaaaa") == (1001, first)
    second = await mgr.ensure("r_bbbbbb")
    assert second != first and second in PORT_RANGE
    assert fake.launched[0][0] == get_settings().runs_dir / "r_aaaaaa" / "app"


async def test_dead_server_is_restarted(env: Path) -> None:
    make_runs(env, "r_aaaaaa")
    fake = Fake()
    mgr = fake.manager()
    await mgr.ensure("r_aaaaaa")
    fake.alive_pids.clear()
    await mgr.ensure("r_aaaaaa")
    assert len(fake.launched) == 2


async def test_idle_over_30_minutes_stops_the_server(env: Path) -> None:
    make_runs(env, "r_aaaaaa", "r_bbbbbb")
    fake = Fake()
    mgr = fake.manager()
    await mgr.ensure("r_aaaaaa")
    await mgr.ensure("r_bbbbbb")
    fake.now = 20 * 60
    mgr.touch("r_bbbbbb")  # activity keeps b alive
    fake.now = 31 * 60
    assert await mgr.reap_idle() == ["r_aaaaaa"]
    assert fake.killed == [1001]
    assert recorded("r_aaaaaa") == (None, None)
    assert mgr.port_of("r_bbbbbb") is not None
    fake.now = 52 * 60
    assert await mgr.reap_idle() == ["r_bbbbbb"]


async def test_start_failure_kills_the_process_and_raises(env: Path) -> None:
    make_runs(env, "r_aaaaaa")
    fake = Fake()
    fake.ready_ok = False
    mgr = fake.manager()
    with pytest.raises(PreviewError):
        await mgr.ensure("r_aaaaaa")
    assert fake.killed == [1001]
    assert recorded("r_aaaaaa") == (None, None)


async def test_missing_app_dir_raises(env: Path) -> None:
    make_runs(env, "r_aaaaaa")
    (get_settings().runs_dir / "r_aaaaaa" / "app").rmdir()
    with pytest.raises(PreviewError):
        await Fake().manager().ensure("r_aaaaaa")


async def test_stop_all_kills_everything(env: Path) -> None:
    make_runs(env, "r_aaaaaa", "r_bbbbbb")
    fake = Fake()
    mgr = fake.manager()
    await mgr.ensure("r_aaaaaa")
    await mgr.ensure("r_bbbbbb")
    await mgr.stop_all()
    assert sorted(fake.killed) == [1001, 1002]
    assert recorded("r_bbbbbb") == (None, None)


NODE = "node.exe" if IS_WINDOWS else "node /app/node_modules/.bin/next start"


def record_previews(*rows: tuple[str, int, int]) -> None:
    with open_session() as session:
        for rid, pid, port in rows:
            run = session.get(Run, rid)
            assert run is not None
            run.preview_pid, run.preview_port = pid, port
        session.commit()


async def test_kill_orphans_kills_node_servers_with_a_listening_port(env: Path) -> None:
    make_runs(env, "r_aaaaaa", "r_bbbbbb", "r_cccccc")
    record_previews(("r_aaaaaa", 555, 4300), ("r_bbbbbb", 556, 4301))
    fake = Fake()
    fake.alive_pids = {555}  # 556 already died: nothing to kill, but the record is cleared
    fake.images = {555: NODE}
    killed = await fake.manager(busy={4300, 4301}).kill_orphans()
    assert killed == [555] and fake.killed == [555]
    for rid in ("r_aaaaaa", "r_bbbbbb", "r_cccccc"):
        assert recorded(rid) == (None, None)


async def test_kill_orphans_spares_a_reused_pid(env: Path) -> None:
    make_runs(env, "r_aaaaaa", "r_bbbbbb")
    record_previews(("r_aaaaaa", 555, 4300), ("r_bbbbbb", 556, 4301))
    fake = Fake()
    fake.alive_pids = {555, 556}
    fake.images = {555: "chrome.exe" if IS_WINDOWS else "/usr/bin/vim", 556: NODE}
    # 555: pid reused by another program. 556: node, but nothing listens on 4301 any more.
    killed = await fake.manager(busy={4300}).kill_orphans()
    assert killed == [] and fake.killed == []
    assert recorded("r_aaaaaa") == (None, None) and recorded("r_bbbbbb") == (None, None)


async def test_concurrent_ensure_gets_distinct_ports(env: Path) -> None:
    make_runs(env, "r_aaaaaa", "r_bbbbbb")
    fake = Fake()
    fake.launch_delay = 0.05  # both picks happen before either server is live
    mgr = fake.manager()
    a, b = await asyncio.gather(mgr.ensure("r_aaaaaa"), mgr.ensure("r_bbbbbb"))
    assert a != b and {a, b} <= set(PORT_RANGE)
    assert not mgr._reserved  # pyright: ignore[reportPrivateUsage]


async def test_failed_start_releases_the_reservation_and_stop_drops_the_lock(env: Path) -> None:
    make_runs(env, "r_aaaaaa")
    fake = Fake()
    fake.ready_ok = False
    mgr = fake.manager()
    with pytest.raises(PreviewError):
        await mgr.ensure("r_aaaaaa")
    assert not mgr._reserved  # pyright: ignore[reportPrivateUsage]
    fake.ready_ok = True
    port = await mgr.ensure("r_aaaaaa")
    assert port == PORT_RANGE[0]
    assert "r_aaaaaa" in mgr._locks  # pyright: ignore[reportPrivateUsage]
    await mgr.stop("r_aaaaaa")
    assert "r_aaaaaa" not in mgr._locks  # pyright: ignore[reportPrivateUsage]


async def test_a_process_that_died_after_the_http_check_is_not_served(env: Path) -> None:
    make_runs(env, "r_aaaaaa")
    fake = Fake()

    async def ready_then_die(port: int, pid: int, timeout_s: float) -> bool:
        fake.alive_pids.discard(pid)  # an unrelated server answered, ours is gone
        return True

    fake.ready = ready_then_die  # type: ignore[method-assign]
    mgr = fake.manager()
    with pytest.raises(PreviewError):
        await mgr.ensure("r_aaaaaa")
    assert mgr.port_of("r_aaaaaa") is None
