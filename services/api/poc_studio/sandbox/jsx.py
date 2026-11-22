"""Deterministic HTML fragment to JSX. Screens are plain markup (no inline styles, handlers or scripts)."""

import re
from html.parser import HTMLParser

VOID = frozenset(
    "area base br col embed hr img input link meta param source track wbr".split()
)  # fmt: skip
_SKIP_CONTENT = frozenset({"script", "style"})
_RENAME = {
    "class": "className", "for": "htmlFor", "tabindex": "tabIndex", "colspan": "colSpan",
    "rowspan": "rowSpan", "readonly": "readOnly", "maxlength": "maxLength", "minlength": "minLength",
    "autocomplete": "autoComplete", "autofocus": "autoFocus", "contenteditable": "contentEditable",
    "crossorigin": "crossOrigin", "datetime": "dateTime", "viewbox": "viewBox", "srcset": "srcSet",
    "spellcheck": "spellCheck", "enctype": "encType", "novalidate": "noValidate",
    "accept-charset": "acceptCharset", "http-equiv": "httpEquiv", "usemap": "useMap",
    "cellpadding": "cellPadding", "cellspacing": "cellSpacing", "allowfullscreen": "allowFullScreen",
    "preserveaspectratio": "preserveAspectRatio", "checked": "defaultChecked", "selected": "defaultSelected",
}  # fmt: skip
_VALUE_TAGS = frozenset({"input", "textarea", "select"})
_ATTR_OK = re.compile(r"^[A-Za-z_:][A-Za-z0-9_:.\-]*$")


def jsx_attr_name(name: str, tag: str = "") -> str | None:
    """React's name for an HTML attribute; None drops it (inline style, event handlers, junk)."""
    low = name.lower()
    if low == "style" or low.startswith("on") or not _ATTR_OK.match(name):
        return None
    if low.startswith(("data-", "aria-")):
        return low
    if low == "value" and tag in _VALUE_TAGS:
        return "defaultValue"
    if low in _RENAME:
        return _RENAME[low]
    if low.startswith(("xlink:", "xml:")):
        prefix, rest = low.split(":", 1)
        return prefix + rest.capitalize()
    if "-" in low:  # SVG presentation attributes: stroke-width -> strokeWidth
        head, *tail = low.split("-")
        return head + "".join(p.capitalize() for p in tail)
    return low


def _text(s: str) -> str:
    return (
        s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        .replace("{", "{'{'}").replace("}", "{'}'}")
    )  # fmt: skip


def _attr_value(s: str) -> str:
    return s.replace("&", "&amp;").replace('"', "&quot;").replace("<", "&lt;").replace(">", "&gt;")


class _Converter(HTMLParser):
    def __init__(self, hrefs: dict[str, str]) -> None:
        super().__init__(convert_charrefs=True)
        self.out: list[str] = []
        self.stack: list[str] = []
        self.skip = 0
        self.hrefs = hrefs
        self.link_text: list[str] | None = None
        self.link_at = -1

    def _open(self, tag: str, attrs: list[tuple[str, str | None]], self_close: bool) -> None:
        parts: list[str] = []
        names: set[str] = set()
        for name, value in attrs:
            jn = jsx_attr_name(name, tag)
            if jn is None or jn in names:
                continue
            names.add(jn)
            parts.append(jn if value is None else f'{jn}="{_attr_value(value)}"')
        self.out.append(f"<{tag}{''.join(' ' + p for p in parts)}{' /' if self_close else ''}>")

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in _SKIP_CONTENT:
            self.skip += 1
            return
        if self.skip:
            return
        if tag in VOID:
            self._open(tag, attrs, True)
            return
        if tag == "a" and not any(n == "href" for n, _ in attrs):
            self.link_at = len(self.out)  # fill the href later, once the label text is known
            self.link_text = []
        self._open(tag, attrs, False)
        self.stack.append(tag)

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self.skip:
            return
        if tag in VOID or tag in _SKIP_CONTENT:
            if tag not in _SKIP_CONTENT:
                self._open(tag, attrs, True)
            return
        self._open(tag, attrs, True)  # `<path/>` and other self-closed SVG shapes

    def handle_endtag(self, tag: str) -> None:
        if self.skip:
            if tag in _SKIP_CONTENT:
                self.skip -= 1
            return
        if tag in VOID or tag not in self.stack:
            return  # `</br>` or a stray close tag
        while self.stack:  # close any element left open inside it (`<li>` without `</li>`)
            top = self.stack.pop()
            if top == "a":
                self._finish_link()
            self.out.append(f"</{top}>")
            if top == tag:
                break

    def _finish_link(self) -> None:
        if self.link_text is None:
            return
        label = " ".join("".join(self.link_text).split()).lower()
        href = self.hrefs.get(label)
        if href is not None and 0 <= self.link_at < len(self.out):
            self.out[self.link_at] = self.out[self.link_at][:-1] + f' href="{href}">'
        self.link_text = None

    def handle_data(self, data: str) -> None:
        if self.skip:
            return
        if self.link_text is not None:
            self.link_text.append(data)
        self.out.append(_text(data))

    def handle_comment(self, data: str) -> None:
        return

    def finish(self) -> str:
        self.close()
        while self.stack:
            top = self.stack.pop()
            if top == "a":
                self._finish_link()
            self.out.append(f"</{top}>")
        return "".join(self.out)


def html_to_jsx(fragment: str, hrefs: dict[str, str] | None = None) -> str:
    """JSX for an HTML fragment. `hrefs` maps a lower-case link label to a route for `<a>` without href."""
    conv = _Converter(hrefs or {})
    conv.feed(fragment)
    return conv.finish()


def page_source(screen_id: str, fragment: str, hrefs: dict[str, str] | None = None) -> str:
    body = html_to_jsx(fragment.strip(), hrefs)
    return (
        "export default function Page() {\n"
        "  return (\n"
        f'    <div className="pf"><div className="sl-{screen_id}">{body}</div></div>\n'
        "  );\n"
        "}\n"
    )
