"""Real npm: build the logistics starter with the fixture screens ported in, serve it, GET it."""

import json
from pathlib import Path

import httpx
import pytest

from poc_studio.agents.port import write_app
from poc_studio.config import get_settings
from poc_studio.llm.provider import FIXTURE_DIR
from poc_studio.preview.manager import PreviewManager, port_is_free
from poc_studio.sandbox import runner
from poc_studio.schemas.screenpack import ScreenPack
from poc_studio.screens.kits import load_kit
from tests.preview.test_manager import make_runs

pytestmark = pytest.mark.slow


async def test_build_serve_get_stop(env: Path) -> None:
    make_runs(env, "r_abcdef")
    pack = ScreenPack.model_validate(
        json.loads((FIXTURE_DIR / "screens.json").read_text(encoding="utf-8"))[-1]
    )
    run_dir = get_settings().runs_dir / "r_abcdef"
    app = await runner.prepare(run_dir, "logistics")
    write_app(app, pack, load_kit("logistics").icons_css, "Acme prototype")
    assert (await runner.install(app)).ok
    built = await runner.build(app, 1)
    assert built.ok, built.log_tail

    mgr = PreviewManager()
    port = await mgr.ensure("r_abcdef")
    try:
        assert 4300 <= port <= 4399
        res = httpx.get(f"http://127.0.0.1:{port}/", timeout=10)
        assert res.status_code == 200 and "<html" in res.text
        assert await mgr.ensure("r_abcdef") == port
    finally:
        await mgr.stop_all()
    assert port_is_free(port)
