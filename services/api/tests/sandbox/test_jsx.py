import json
import re

import pytest
from lxml import etree

from poc_studio.agents.port import route_file
from poc_studio.llm.provider import FIXTURE_DIR
from poc_studio.sandbox.jsx import html_to_jsx, page_source
from poc_studio.schemas.screenpack import ScreenPack

PACK = ScreenPack.model_validate(json.loads((FIXTURE_DIR / "screens.json").read_text(encoding="utf-8"))[-1])
JSX_ONLY = re.compile(r"\{'[{}]'\}")


def _as_xml(jsx: str) -> etree._Element:
    """JSX with the `{'{'}` escapes undone and entities swapped, parsed in XML mode."""
    text = JSX_ONLY.sub("", jsx)
    for ent in ("nbsp", "copy", "middot", "mdash", "ndash", "times", "rarr", "larr", "hellip"):
        text = text.replace(f"&{ent};", "x")
    return etree.fromstring(text.encode("utf-8"))


@pytest.mark.parametrize("screen", PACK.screens, ids=lambda s: s.id)
def test_every_screen_converts_to_wellformed_jsx(screen) -> None:
    jsx = html_to_jsx(screen.html)
    assert "class=" not in jsx and "for=" not in jsx and "style=" not in jsx and "<!--" not in jsx
    root = _as_xml(f"<root>{jsx}</root>")  # balanced tags or the parse fails
    assert len(root) >= 1
    assert re.search(r"<(input|img|br|hr)\b[^>]*[^/]>", jsx) is None  # void tags are self-closed
    src = page_source(screen.id, screen.html)
    assert src.startswith("export default function Page()")
    assert f'className="sl-{screen.id}"' in src
    _as_xml(re.search(r"return \(\n(.*)\n  \);", src, re.S).group(1))  # pyright: ignore[reportOptionalMemberAccess]


def test_attribute_and_text_rules() -> None:
    out = html_to_jsx(
        '<!-- c --><label for="a" class="x" style="color:red" onclick="f()" data-anchor="k" aria-label="L">'
        'a { b } &amp; <c</label><input type="text" value="v" tabindex="1" disabled><br>'
        '<svg viewbox="0 0 1 1"><path stroke-width="2" d="M0"/></svg>'
        "<script>alert(1)</script><ul><li>one<li>two</ul>"
    )
    assert 'htmlFor="a"' in out and 'className="x"' in out
    assert "style" not in out and "onclick" not in out and "alert" not in out and "<!--" not in out
    assert 'data-anchor="k"' in out and 'aria-label="L"' in out
    assert "{'{'}" in out and "{'}'}" in out and "&amp;" in out
    assert "<input" in out and 'defaultValue="v"' in out and 'tabIndex="1"' in out and " disabled" in out
    assert "<br />" in out and 'viewBox="0 0 1 1"' in out and 'strokeWidth="2"' in out
    assert out.count("<li>") == out.count("</li>") == 2


def test_label_links_get_the_route() -> None:
    out = html_to_jsx('<a class="rail-link">Fleet <span>x</span></a><a>Other</a>', {"fleet x": "/fleet"})
    assert 'href="/fleet"' in out and out.count("href") == 1


def test_route_files() -> None:
    assert route_file("/") == "app/page.tsx"
    assert route_file("/fleet-map") == "app/fleet-map/page.tsx"
    with pytest.raises(ValueError):
        route_file("/../x")


def _balanced(jsx: str) -> bool:
    """Every brace in text is one of the two escape tokens; nothing stray is left after removing them."""
    rest = JSX_ONLY.sub("", jsx)
    return "{" not in rest and "}" not in rest


@pytest.mark.parametrize(
    "src",
    [
        "a {b} c", "{{x}}", "}}", "&#123;", "&#125;&#125;", "x{", "}{", "<p>{a}</p><b>}</b>",
        "&lbrace;x&rbrace;",
    ],
)
def test_braces_are_balanced_jsx_expressions(src: str) -> None:
    out = html_to_jsx(src)
    assert _balanced(out), out
    assert out.count("{'{'}") == src.count("{") + src.count("&#123;") + src.count("&lbrace;")


def test_invalid_tag_names_are_dropped_but_text_kept() -> None:
    out = html_to_jsx("<p>a</p><x{y}>kept {b}</x{y}><1a>t</1a>")
    assert "x{y}" not in out and "<1a" not in out
    assert "kept" in out and _balanced(out) and "<p>a</p>" in out
