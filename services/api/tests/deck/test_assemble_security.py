"""Deck self-containment: the assembler rejects every way a screen could reach outside the file."""

import json
import re

import pytest

from poc_studio.media.assemble import DeckNotSelfContained, assemble
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.screenpack import ScreenPack

PNG = "data:image/png;base64,AAAA"


def _dk_data(html: str) -> dict:
    raw = re.search(r'id="dk-data">(.*?)</script>', html, re.S)
    assert raw
    return json.loads(raw.group(1))


# --- logo ----------------------------------------------------------------------------------------
def test_plan_logo_markup_is_ignored(pack: ScreenPack, plan: DeckPlan) -> None:
    evil = plan.model_copy(update={"logo": "<img src=x onerror=alert(1)>"})
    html = assemble(pack, evil, None)
    assert _dk_data(html)["logo"] == ""
    assert "onerror" not in html


def test_plan_logo_markup_is_ignored_even_with_a_uri(pack: ScreenPack, plan: DeckPlan) -> None:
    evil = plan.model_copy(update={"logo": "<img src=x onerror=alert(1)>"})
    logo = _dk_data(assemble(pack, evil, PNG))["logo"]
    assert logo == f'<img src="{PNG}" alt="Client logo">'


@pytest.mark.parametrize(
    "uri",
    [
        "https://example.com/l.png",
        "data:text/html;base64,AAAA",
        'data:image/png;base64,AA"onerror="x',
        "javascript:alert(1)",
        "data:image/gif;base64,AAAA",
    ],
)
def test_bad_logo_uri_raises(pack: ScreenPack, plan: DeckPlan, uri: str) -> None:
    with pytest.raises(DeckNotSelfContained):
        assemble(pack, plan, uri)


@pytest.mark.parametrize("mime", ["png", "jpeg", "svg+xml", "webp"])
def test_allowed_logo_types(pack: ScreenPack, plan: DeckPlan, mime: str) -> None:
    assert f"data:image/{mime};base64,AAAA" in assemble(pack, plan, f"data:image/{mime};base64,AAAA")


# --- screen html -----------------------------------------------------------------------------------
HTML_VECTORS = {
    "script": "<script>1</script>",
    "iframe": "<iframe src='about:blank'></iframe>",
    "object": "<object data='x'></object>",
    "embed": "<embed src='x'>",
    "meta": "<meta http-equiv='refresh' content='0;url=//e.com'>",
    "base": "<base href='data:,'>",
    "form": "<form action='#'></form>",
    "link": "<link rel='stylesheet' href='x.css'>",
    "on-attr": "<b onclick='x()'>b</b>",
    "on-attr-upper": "<b ONMOUSEOVER = 'x()'>b</b>",
    "template-close": "</template><img src=x>",
    "template-open": "<template><b>x</b></template>",
    "js-url": "<a href='javascript:alert(1)'>x</a>",
    "js-url-split": "<a href=' java\tscript:alert(1)'>x</a>",
    "src": "<img src='https://e.com/x.png'>",
    "src-proto-relative": "<img src='//e.com/x.png'>",
    "src-control-chars": "<img src='ht\ntp://e.com/x.png'>",
    "href": "<a href='http://e.com'>x</a>",
    "xlink": "<svg><use xlink:href='http://e.com/s.svg#a'/></svg>",
    "srcset": "<img srcset='a.png 1x, https://e.com/b.png 2x'>",
    "poster": "<video poster='https://e.com/p.png'></video>",
    "data-attr": "<div data='https://e.com/x'></div>",
    "action": "<button formaction='https://e.com'>x</button>",
    "srcdoc": "<div srcdoc='<b>x</b>'></div>",
    "background": "<table background='https://e.com/b.png'></table>",
}


@pytest.mark.parametrize("name", sorted(HTML_VECTORS))
def test_screen_html_vectors_raise(pack: ScreenPack, plan: DeckPlan, name: str) -> None:
    bad = pack.model_copy(deep=True)
    bad.screens[1].html += HTML_VECTORS[name]
    with pytest.raises(DeckNotSelfContained, match=re.escape(bad.screens[1].id)):
        assemble(bad, plan, None)


def test_data_uri_in_src_is_fine(pack: ScreenPack, plan: DeckPlan) -> None:
    ok = pack.model_copy(deep=True)
    ok.screens[0].html += f'<img src="{PNG}" alt="">'
    assert PNG in assemble(ok, plan, None)


# --- screen script ---------------------------------------------------------------------------------
SCRIPT_VECTORS = [
    "fetch('/x')",
    "new XMLHttpRequest()",
    "new WebSocket('ws://x')",
    "new EventSource('/e')",
    "import('x.js')",
    "importScripts('x.js')",
    "navigator.sendBeacon('/x')",
    "location = '/x'",
    "window.location.href = '/x'",
    "location.assign('/x')",
    "eval('1')",
    "new Function('1')()",
    "document.cookie",
    "localStorage.x",
    "var u = 'https://e.com'",
]


@pytest.mark.parametrize("script", SCRIPT_VECTORS)
def test_screen_script_vectors_raise(pack: ScreenPack, plan: DeckPlan, script: str) -> None:
    bad = pack.model_copy(deep=True)
    bad.screens[2].script = script
    with pytest.raises(DeckNotSelfContained, match=re.escape(bad.screens[2].id)):
        assemble(bad, plan, None)


def test_script_breakers_are_escaped(pack: ScreenPack, plan: DeckPlan) -> None:
    p = pack.model_copy(deep=True)
    p.screens[0].script = "var a='<!-- <script> </script>';"
    html = assemble(p, plan, None)
    assert r"<\!--" in html and r"<\script" in html and r"<\/script>" in html
    assert "<!-- <script>" not in html


def test_json_breakers_are_escaped(pack: ScreenPack, plan: DeckPlan) -> None:
    tricky = plan.model_copy(update={"title": "A <script> <!-- b"})
    html = assemble(pack, tricky, None)
    raw = re.search(r'id="dk-data">(.*?)</script>\n', html, re.S)
    assert raw and "<script" not in raw.group(1).lower() and "<!--" not in raw.group(1)
    assert json.loads(raw.group(1))["title"] == "A <script> <!-- b"


# --- css ---------------------------------------------------------------------------------------------
CSS_VECTORS = [
    ".x{background:url(https://e.com/a.png)}",
    ".x{background:url( 'http://e.com/a.png' )}",
    ".x{background:url(//e.com/a.png)}",
    ".x{background:url(javascript:alert(1))}",
    "@import 'x.css';",
    '.x{background:image-set("https://e.com/a.png" 1x)}',
    ".x{content:'http://e.com'}",
]


@pytest.mark.parametrize("css", CSS_VECTORS)
@pytest.mark.parametrize("where", ["product", "step", "extra"])
def test_css_vectors_raise(pack: ScreenPack, plan: DeckPlan, css: str, where: str) -> None:
    bad = pack.model_copy(deep=True)
    extra = ""
    if where == "product":
        bad.product_css += css
    elif where == "step":
        bad.screens[0].step_css += css
    else:
        extra = css
    with pytest.raises(DeckNotSelfContained):
        assemble(bad, plan, None, extra_css=extra)


def test_namespace_inside_data_uri_is_fine(pack: ScreenPack, plan: DeckPlan) -> None:
    ok = (
        ".pf .ic{mask:url(\"data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg'/>\")}"
        ".pf .ic2{mask:url(data:image/svg+xml;utf8,%3Csvg xmlns=%27http%3A//www.w3.org/2000/svg%27/%3E)}"
    )
    assert "ic2" in assemble(pack, plan, None, extra_css=ok)
