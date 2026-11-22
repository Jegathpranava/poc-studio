import pytest
from pydantic import ValidationError

from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.screenpack import ScreenPack


def _screen(i: int) -> dict:
    return {
        "id": f"s-{i}",
        "label": f"Screen {i}",
        "route": f"/s-{i}",
        "html": '<div class="a"><i class="x"></i><i class="y"></i><i class="z"></i></div>',
        "step_css": f".pf.sl-s-{i}[data-step='1'] .x {{ opacity: 1; }}",
        "anchors": [{"selector": s, "purpose": "p"} for s in (".x", ".y", ".z")],
        "play": i == 0,
    }


def _pack(n: int) -> dict:
    return {
        "app_class": "fleet",
        "accent": "#0a7cff",
        "product_css": ".pf .fleet .a { color: red; }",
        "screens": [_screen(i) for i in range(n)],
    }


def test_screenpack_valid() -> None:
    assert len(ScreenPack.model_validate(_pack(6)).screens) == 6


def test_screenpack_five_screens_fails() -> None:
    with pytest.raises(ValidationError):
        ScreenPack.model_validate(_pack(5))


def test_screenpack_anchor_must_match_html() -> None:
    data = _pack(6)
    data["screens"][0]["anchors"][0]["selector"] = ".missing"
    with pytest.raises(ValidationError):
        ScreenPack.model_validate(data)


def _slide(i: int, kind: str = "area") -> dict:
    return {
        "id": f"sl{i}",
        "kind": kind,
        "title": "T",
        "caption": "C",
        "steps": [{"title": "t", "caption": "c", "spotlight": ".x"}] * 3 if kind == "area" else [],
    }


def _plan(n: int) -> dict:
    slides = [
        _slide(0, "welcome"),
        *[_slide(i) for i in range(1, n - 2)],
        _slide(n - 2, "play"),
        _slide(n - 1, "close"),
    ]
    return {
        "title": "Deck",
        "accent": "#0a7cff",
        "slides": slides,
        "exec_summary_md": "x",
        "user_flows_md": "y",
    }


def test_deckplan_valid() -> None:
    assert len(DeckPlan.model_validate(_plan(10)).slides) == 10


def test_deckplan_too_few_slides_fails() -> None:
    with pytest.raises(ValidationError):
        DeckPlan.model_validate(_plan(8))
