import tempfile
from pathlib import Path

import pytest

from poc_studio.schemas.deck import DeckPlan

pytestmark = pytest.mark.browser


def test_deck_contract(browser_name_and_browser, deck_html: str, plan: DeckPlan, tmp_path: Path) -> None:
    label, browser = browser_name_and_browser
    deck = tmp_path / "deck.html"
    deck.write_text(deck_html, encoding="utf-8")

    page = browser.new_page(viewport={"width": 1280, "height": 720})
    messages: list[str] = []
    page.on("console", lambda m: messages.append(m.text))
    page.on("pageerror", lambda e: messages.append(f"pageerror: {e}"))
    page.goto(deck.as_uri())
    page.wait_for_function("window.__deck && window.__deck.ready === true", timeout=5000)

    # stage is 1280x720 before scaling
    size = page.evaluate(
        "(() => { const s = getComputedStyle(document.getElementById('dk-stage'));"
        " return [s.width, s.height]; })()"
    )
    assert size == ["1280px", "720px"]

    # every step of every slide resolves its spotlight (the runtime logs when it does not)
    for i, slide in enumerate(plan.slides, start=1):
        for n in range(1, max(1, len(slide.steps)) + 1):
            page.evaluate(f"window.__deck.go({i}, {n})")
            assert page.evaluate("window.__deck.position()") == [i, n]
            page.wait_for_timeout(30)

    # deep link
    page.goto(deck.as_uri() + "#2.1")
    page.reload()
    page.wait_for_function("window.__deck && window.__deck.ready === true", timeout=5000)
    assert page.evaluate("window.__deck.position()") == [2, 1]

    bad = [m for m in messages if "Spotlight target not found" in m or "Invalid spotlight selector" in m]
    assert not bad, bad
    assert not [m for m in messages if m.startswith("pageerror")], messages

    shot = Path(tempfile.gettempdir()) / "poc-deck-contract.png"
    page.goto(deck.as_uri() + "#3.2")
    page.reload()
    page.wait_for_function("window.__deck.ready === true", timeout=5000)
    page.wait_for_timeout(600)
    page.screenshot(path=str(shot))
    assert shot.stat().st_size > 5000
    print(f"\nbrowser={label} screenshot={shot}")
    page.close()
