"""Deck assembler (spec 7a): deterministic, no LLM. Merges the vendored runtime and chrome CSS with a
ScreenPack and a DeckPlan into one self-contained HTML document."""

import json
import re
from functools import cache
from html import escape
from pathlib import Path

from lxml import html as lxml_html

from poc_studio.safety import (
    BARE_URL,
    CSS_DATA_URL,
    CSS_IMAGE_SET,
    CSS_URL_EXTERNAL,
    FORBIDDEN_TAGS,
    SCRIPT_BANNED,
    STRIP,
    TEMPLATE_TAG,
    URL_ATTRS,
    url_problem,
)
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

_LOGO = re.compile(r"^data:image/(?:png|jpeg|svg\+xml|webp);base64,[A-Za-z0-9+/]+={0,2}$")
_LOGO_ALT = "Client logo"
class DeckNotSelfContained(ValueError):
    """The assembled deck references something outside the file."""


@cache
def _read(name: str) -> str:
    return (RUNTIME_DIR / name).read_text(encoding="utf-8")


def _json_for_script(data: object) -> str:
    text = json.dumps(data, ensure_ascii=False).replace("</", r"<\/").replace("<!--", r"<\u0021--")
    return re.sub(
        r"<(s)(cript)", lambda m: f"<\\u{ord(m.group(1)):04x}{m.group(2)}", text, flags=re.IGNORECASE
    )


def _script_safe(js: str) -> str:
    js = re.sub(r"</(script)", r"<\/\1", js, flags=re.IGNORECASE)
    js = js.replace("<!--", r"<\!--")
    return re.sub(r"<(script)", r"<\\\1", js, flags=re.IGNORECASE)


def _check_html(screen_id: str, markup: str) -> None:
    def fail(reason: str) -> DeckNotSelfContained:
        return DeckNotSelfContained(f"screen {screen_id!r}: {reason}")

    if (tag := FORBIDDEN_TAGS.search(markup)) is not None:
        raise fail(f"<{tag.group(1).lower()}> elements are not allowed")
    if TEMPLATE_TAG.search(markup):
        raise fail("<template> tags are not allowed (they could close the screen's own template)")
    root = lxml_html.fromstring(f"<div>{markup}</div>")
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        for name, value in el.attrib.items():
            lname = name.lower()
            if lname.startswith("on"):
                raise fail(f"event handler attribute {lname}= on <{el.tag}>")
            if lname == "srcdoc":  # inline markup, not a URL: never allowed
                raise fail(f"<{el.tag} srcdoc=...> embeds a document")
            if lname in URL_ATTRS:
                if (problem := url_problem(lname, value)) is not None:
                    raise fail(f"<{el.tag} {lname}=...> is {problem}")
            elif "javascript:" in STRIP.sub("", value).lower():
                raise fail(f"<{el.tag} {lname}=...> holds a javascript: URL")


def _check_script(screen_id: str, js: str) -> None:
    for name, pattern in SCRIPT_BANNED:
        if pattern.search(js):
            raise DeckNotSelfContained(f"screen {screen_id!r}: script uses {name}")


def _check_css(where: str, css: str) -> None:
    if CSS_URL_EXTERNAL.search(css):
        raise DeckNotSelfContained(f"{where}: css url() loads an external or javascript: target")
    if "@import" in css.lower():
        raise DeckNotSelfContained(f"{where}: css @import")
    if CSS_IMAGE_SET.search(css):
        raise DeckNotSelfContained(f"{where}: css image-set() loads an external target")
    if BARE_URL.search(CSS_DATA_URL.sub("url()", css)):
        raise DeckNotSelfContained(f"{where}: css holds an http(s) URL")


def _validate_inputs(pack: ScreenPack, extra_css: str) -> None:
    _check_css("product css", pack.product_css)
    _check_css("extra css", extra_css)
    for s in pack.screens:
        _check_html(s.id, s.html)
        _check_css(f"screen {s.id!r} step css", s.step_css)
        if s.script:
            _check_script(s.id, s.script)


def _validate(document: str) -> None:
    """Last look at the assembled file: the skeleton and logo must not load anything either."""
    root = lxml_html.fromstring(document)
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        for attr in URL_ATTRS:
            value = el.get(attr)
            if value is not None and (problem := url_problem(attr, value)) is not None:
                raise DeckNotSelfContained(f"<{el.tag} {attr}={value[:80]!r}> is {problem}")


def assemble(
    pack: ScreenPack,
    plan: DeckPlan,
    logo_data_uri: str | None,
    extra_css: str = "",
) -> str:
    """Return the deck as one HTML string. `extra_css` carries the kit icons.css."""
    _validate_inputs(pack, extra_css)
    data = plan.model_dump(by_alias=True)
    data["accent"] = plan.accent
    data["logo"] = ""  # DeckPlan.logo is never trusted: only a validated data: URI becomes an <img>
    if logo_data_uri:
        if not _LOGO.fullmatch(logo_data_uri):
            raise DeckNotSelfContained("logo must be a base64 data:image/(png|jpeg|svg+xml|webp) URI")
        data["logo"] = f'<img src="{escape(logo_data_uri, quote=True)}" alt="{_LOGO_ALT}">'

    css = "\n".join(
        [_read("chrome.css"), pack.product_css, extra_css, *(s.step_css for s in pack.screens)]
    ).replace("</style", r"<\/style")
    templates = "\n".join(f'<template id="tpl-{s.id}">{s.html}</template>' for s in pack.screens)
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
