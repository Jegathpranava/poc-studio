"""Deck assembler (spec 7a): deterministic, no LLM. Merges the vendored runtime and chrome CSS with a
ScreenPack and a DeckPlan into one self-contained HTML document."""

import json
import re
from functools import cache
from html import escape
from pathlib import Path

from lxml import html as lxml_html

from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.screenpack import ScreenPack

RUNTIME_DIR = Path(__file__).parent / "deck_runtime"

_BODY_SKELETON = (
    '<div id="dk-viewport"><div id="dk-stage" role="application" aria-roledescription="presentation">'
    '<div class="dk-bar" id="dk-bar"><button class="dk-btn" id="dk-back" type="button">\u2190 Back</button>'
    '<div class="dk-progress" aria-hidden="true"><i></i></div><span class="dk-count" id="dk-count"></span>'
    '<button class="dk-btn" id="dk-theme" type="button">Dark</button>'
    '<button class="dk-btn" id="dk-fs" type="button" title="Full screen (F)">Full screen</button>'
    '<button class="dk-btn primary" id="dk-next" type="button">Next \u2192</button></div></div></div>'
    '<div class="dk-rotate">Rotate your device for a larger view.</div>'
)

_URL_ATTRS = ("src", "href", "xlink:href", "srcset", "poster")
_EXTERNAL = re.compile(r"^\s*(https?:)?//", re.IGNORECASE)
_CSS_EXTERNAL = re.compile(r"url\(\s*['\"]?\s*(https?:)?//|@import", re.IGNORECASE)


class DeckNotSelfContained(ValueError):
    """The assembled deck references something outside the file."""


@cache
def _read(name: str) -> str:
    return (RUNTIME_DIR / name).read_text(encoding="utf-8")


def _json_for_script(data: object) -> str:
    text = json.dumps(data, ensure_ascii=False)
    return text.replace("</", r"<\/").replace("<!--", r"<\u0021--")


def _script_safe(js: str) -> str:
    return re.sub(r"</(script)", r"<\/\1", js, flags=re.IGNORECASE)


def _validate(document: str) -> None:
    root = lxml_html.fromstring(document)
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        for attr in _URL_ATTRS:
            value = el.get(attr)
            if value is not None and _EXTERNAL.match(value):
                raise DeckNotSelfContained(f"<{el.tag} {attr}={value[:80]!r}> is external")
        if el.tag == "style" and el.text and _CSS_EXTERNAL.search(el.text):
            raise DeckNotSelfContained("a <style> block imports or loads an external URL")
        style = el.get("style")
        if style and _CSS_EXTERNAL.search(style):
            raise DeckNotSelfContained(f"inline style on <{el.tag}> loads an external URL")


def assemble(
    pack: ScreenPack,
    plan: DeckPlan,
    logo_data_uri: str | None,
    extra_css: str = "",
) -> str:
    """Return the deck as one HTML string. `extra_css` carries the kit icons.css."""
    data = plan.model_dump(by_alias=True)
    data["accent"] = plan.accent
    if logo_data_uri:
        if not logo_data_uri.startswith("data:"):
            raise DeckNotSelfContained("logo must be a data: URI")
        uri, alt = escape(logo_data_uri, quote=True), escape(plan.title, quote=True)
        data["logo"] = f'<img src="{uri}" alt="{alt}">'

    css = "\n".join(
        [_read("chrome.css"), pack.product_css, extra_css, *(s.step_css for s in pack.screens)]
    ).replace("</style", r"<\/style")
    templates = "\n".join(
        f'<template id="tpl-{s.id}">{s.html}</template>' for s in pack.screens
    )
    scripts = "".join(
        f'window.__dkScripts["{s.id}"]=function(root,api){{{_script_safe(s.script)}\n}};\n'
        for s in pack.screens
        if s.script
    )
    document = (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{escape(plan.title)}</title>\n<style>\n{css}\n</style></head>\n<body>\n"
        f"{_BODY_SKELETON}\n{templates}\n"
        f'<script type="application/json" id="dk-data">{_json_for_script(data)}</script>\n'
        f"<script>window.__dkScripts={{}};\n{scripts}</script>\n"
        f"<script>\n{_script_safe(_read('runtime.js'))}\n</script>\n</body></html>\n"
    )
    _validate(document)
    return document
