import re
from pathlib import Path
from typing import Any

import pytest
from sqlalchemy import select

from poc_studio.db.models import Artifact
from poc_studio.db.session import open_session
from poc_studio.llm.client import set_provider
from poc_studio.schemas.deck import DeckPlan
from tests.agents.test_screens import Recorder
from tests.deck.conftest import browser_name_and_browser  # noqa: F401 - fixture reused as is
from tests.graph.conftest import create_run, wait_status


def _full_run(client_for: Any) -> str:
    set_provider(Recorder())
    try:
        with client_for() as client:
            run_id = create_run(client)
            wait_status(client, run_id, "waiting_gate1")
            client.post(f"/api/runs/{run_id}/gates/scope", json={"decision": "approve"})
            wait_status(client, run_id, "waiting_gate2")
            return run_id
    finally:
        set_provider(None)


def _deck_files(env: Path, run_id: str) -> tuple[Path, DeckPlan]:
    with open_session() as s:
        rows = list(s.scalars(select(Artifact).where(Artifact.run_id == run_id, Artifact.type == "deck")))
    html = next(a.path for a in rows if a.path.endswith(".html"))
    plan = next(a.path for a in rows if a.path.endswith(".json"))
    return (
        env / "runs" / html,
        DeckPlan.model_validate_json((env / "runs" / plan).read_text(encoding="utf-8")),
    )


def test_graph_run_assembles_a_self_contained_deck(client_for, env) -> None:
    run_id = _full_run(client_for)
    html_path, plan = _deck_files(env, run_id)
    html = html_path.read_text(encoding="utf-8")
    assert html_path.name.startswith("weekly-sales-dashboard") and html.startswith("<!doctype html>")
    assert not re.search(r"""\b(?:src|href)\s*=\s*["']?\s*(?:https?:)?//""", html, re.IGNORECASE)
    assert "http" not in " ".join(re.findall(r"""\b(?:src|href)\s*=\s*["'][^"']*""", html, re.IGNORECASE))
    screen_slides = [s for s in plan.slides if s.kind in ("overview", "area")]
    assert len(screen_slides) >= 5
    for s in screen_slides:
        assert f'id="tpl-{s.id}"' in html


@pytest.mark.browser
def test_assembled_deck_runs_every_step(client_for, env, browser_name_and_browser) -> None:  # noqa: F811
    _, browser = browser_name_and_browser
    run_id = _full_run(client_for)
    html_path, plan = _deck_files(env, run_id)

    page = browser.new_page(viewport={"width": 1280, "height": 720})
    messages: list[str] = []
    page.on("console", lambda m: messages.append(m.text))
    page.on("pageerror", lambda e: messages.append(f"pageerror: {e}"))
    page.goto(html_path.as_uri())
    page.wait_for_function("window.__deck && window.__deck.ready === true", timeout=5000)
    for i, slide in enumerate(plan.slides, start=1):
        for n in range(1, max(1, len(slide.steps)) + 1):
            page.evaluate(f"window.__deck.go({i}, {n})")
            assert page.evaluate("window.__deck.position()") == [i, n]
            page.wait_for_timeout(30)
    page.close()
    assert not [m for m in messages if "Spotlight target not found" in m or "Invalid spotlight" in m], (
        messages
    )
    assert not [m for m in messages if m.startswith("pageerror")], messages
