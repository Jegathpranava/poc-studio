import json
from pathlib import Path

import pytest

from poc_studio.media.assemble import assemble
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.screenpack import ScreenPack

FIXTURES = Path(__file__).parent.parent / "fixtures" / "deck"


@pytest.fixture(scope="session")
def pack() -> ScreenPack:
    return ScreenPack.model_validate_json((FIXTURES / "pack.json").read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def plan() -> DeckPlan:
    return DeckPlan.model_validate(json.loads((FIXTURES / "plan.json").read_text(encoding="utf-8")))


@pytest.fixture(scope="session")
def icons_css() -> str:
    return (FIXTURES / "icons.css").read_text(encoding="utf-8")


@pytest.fixture(scope="session")
def deck_html(pack: ScreenPack, plan: DeckPlan, icons_css: str) -> str:
    return assemble(pack, plan, None, extra_css=icons_css)


@pytest.fixture(scope="module")
def browser_name_and_browser():
    """Launch Chromium: bundled, then system Chrome, then Edge; skip when none starts."""
    sync_playwright = pytest.importorskip("playwright.sync_api").sync_playwright
    with sync_playwright() as p:
        candidates = (("bundled", {}), ("chrome", {"channel": "chrome"}), ("msedge", {"channel": "msedge"}))
        for label, kwargs in candidates:
            try:
                browser = p.chromium.launch(**kwargs)
            except Exception:  # noqa: BLE001 - any launch failure means try the next one
                continue
            yield label, browser
            browser.close()
            return
        pytest.skip("no browser")
