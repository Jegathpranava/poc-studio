import json
import re

import pytest

from poc_studio.media.assemble import DeckNotSelfContained, assemble
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.screenpack import ScreenPack


def test_contains_every_template(deck_html: str, pack: ScreenPack) -> None:
    for s in pack.screens:
        assert f'<template id="tpl-{s.id}">' in deck_html
    assert deck_html.startswith("<!doctype html>")
    assert 'id="dk-stage"' in deck_html and "window.__deck" in deck_html


def test_no_external_src_or_href(deck_html: str) -> None:
    assert not re.findall(r"""(?:src|href)\s*=\s*["']?\s*(?:https?:)?//""", deck_html, re.IGNORECASE)


def test_external_image_raises(pack: ScreenPack, plan: DeckPlan) -> None:
    bad = pack.model_copy(deep=True)
    bad.screens[0].html += '<img src="https://example.com/x.png">'
    with pytest.raises(DeckNotSelfContained):
        assemble(bad, plan, None)


def test_external_css_url_raises(pack: ScreenPack, plan: DeckPlan) -> None:
    bad = pack.model_copy(update={"product_css": pack.product_css + ".x{background:url(https://e.com/a.png)}"})
    with pytest.raises(DeckNotSelfContained):
        assemble(bad, plan, None)


def test_external_logo_raises(pack: ScreenPack, plan: DeckPlan) -> None:
    with pytest.raises(DeckNotSelfContained):
        assemble(pack, plan, "https://example.com/logo.png")


def test_dk_data_round_trips(deck_html: str, plan: DeckPlan) -> None:
    raw = re.search(r'<script type="application/json" id="dk-data">(.*?)</script>', deck_html, re.S)
    assert raw
    assert DeckPlan.model_validate(json.loads(raw.group(1))) == plan


def test_script_and_logo_embedding(pack: ScreenPack, plan: DeckPlan) -> None:
    p = pack.model_copy(deep=True)
    p.screens[0].script = "api.onStep(function(){});"
    html = assemble(p, plan, "data:image/png;base64,AAAA")
    assert f'window.__dkScripts["{p.screens[0].id}"]=function(root,api){{api.onStep' in html
    assert "data:image/png;base64,AAAA" in html


def test_dk_data_escapes_script_breakers(pack: ScreenPack, plan: DeckPlan) -> None:
    tricky = plan.model_copy(update={"title": "A </script><!-- b"})
    html = assemble(pack, tricky, None)
    raw = re.search(r'id="dk-data">(.*?)</script>', html, re.S)
    assert raw and "</" not in raw.group(1) and "<!--" not in raw.group(1)
    assert json.loads(raw.group(1))["title"] == "A </script><!-- b"
