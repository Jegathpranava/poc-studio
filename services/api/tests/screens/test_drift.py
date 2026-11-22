"""The validator and the assembler share `poc_studio.safety`: what one rejects, the other rejects too."""

import copy
import json
from collections.abc import Callable
from typing import Any

import pytest

from poc_studio.llm.provider import FIXTURE_DIR
from poc_studio.media.assemble import DeckNotSelfContained, assemble
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.screenpack import ScreenPack
from poc_studio.screens.kits import load_kit
from poc_studio.screens.validate import validate

KIT = load_kit("logistics")
VALID: dict[str, Any] = json.loads((FIXTURE_DIR / "screens.json").read_text(encoding="utf-8"))[1]
PLAN = DeckPlan.model_validate(json.loads((FIXTURE_DIR / "pitch.json").read_text(encoding="utf-8"))[1])


def _screen_html(extra: str) -> Callable[[dict[str, Any]], None]:
    def change(d: dict[str, Any]) -> None:
        d["screens"][0]["html"] += extra

    return change


def _product_css(extra: str) -> Callable[[dict[str, Any]], None]:
    def change(d: dict[str, Any]) -> None:
        d["product_css"] += "\n" + extra

    return change


def _script(js: str) -> Callable[[dict[str, Any]], None]:
    def change(d: dict[str, Any]) -> None:
        d["screens"][0]["script"] = js

    return change


BAD: dict[str, Callable[[dict[str, Any]], None]] = {
    "external url()": _product_css(".pf .x { background: url(https://evil.test/a.png); }"),
    "protocol-relative url()": _product_css(".pf .x { background: url(//evil.test/a.png); }"),
    "image-set": _product_css('.pf .x { background-image: image-set("https://evil.test/a.png" 1x); }'),
    "@import": _product_css('@import "https://evil.test/a.css";'),
    "script fetch": _script("fetch('/api/x')"),
    "onclick": _screen_html('<button onclick="alert(1)">x</button>'),
    "javascript: href": _screen_html('<a href="javascript:alert(1)">x</a>'),
    "iframe": _screen_html('<iframe src="data:text/html,x"></iframe>'),
    "external img": _screen_html('<img src="https://evil.test/x.png" alt="">'),
}


def _codes(data: dict[str, Any]) -> set[str]:
    return {i.code for i in validate(ScreenPack.model_validate(data), KIT)}


def test_the_baseline_is_clean_on_both_sides() -> None:
    assert _codes(VALID) == set()
    assemble(ScreenPack.model_validate(VALID), PLAN, logo_data_uri=None, extra_css=KIT.icons_css)


@pytest.mark.parametrize("name", list(BAD))
def test_validate_and_assemble_reject_the_same_bad_pack(name: str) -> None:
    data = copy.deepcopy(VALID)
    BAD[name](data)
    assert _codes(data), f"validate() missed: {name}"
    with pytest.raises(DeckNotSelfContained):
        assemble(ScreenPack.model_validate(data), PLAN, logo_data_uri=None, extra_css=KIT.icons_css)


def test_style_is_forbidden_by_the_validator_only() -> None:
    data = copy.deepcopy(VALID)
    _screen_html("<style>.pf .x { color: red; }</style>")(data)
    assert "forbidden_element" in _codes(data)  # screens carry no inline style blocks
