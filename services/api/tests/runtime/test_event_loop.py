import asyncio
import sys

import pytest

from poc_studio.event_loop import loop_factory


def test_loop_can_start_subprocesses() -> None:
    """uvicorn --reload on Windows otherwise picks a SelectorEventLoop: this raises NotImplementedError."""

    async def child() -> bytes:
        proc = await asyncio.create_subprocess_exec(
            sys.executable, "-c", "print('ok')", stdout=asyncio.subprocess.PIPE
        )
        out, _ = await proc.communicate()
        return out

    assert asyncio.run(child(), loop_factory=loop_factory).strip() == b"ok"


@pytest.mark.skipif(sys.platform != "win32", reason="the Proactor loop exists only on Windows")
def test_windows_gets_the_proactor_loop() -> None:
    loop = loop_factory()
    try:
        assert isinstance(loop, asyncio.ProactorEventLoop)
    finally:
        loop.close()


def test_dev_script_uses_the_loop() -> None:
    from pathlib import Path

    dev = (Path(__file__).resolve().parents[4] / "scripts" / "dev.mjs").read_text(encoding="utf-8")
    assert '"--loop", "poc_studio.event_loop:loop_factory"' in dev
