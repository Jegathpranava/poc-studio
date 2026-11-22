"""Stricter ScreenPack checks (spec 7a/7b) beyond the schema. They mirror what the deck assembler rejects,
so a bad pack goes back to the model before the assembler or the port ever sees it."""

import re

from lxml import html as lxml_html
from pydantic import BaseModel

from poc_studio.schemas.screenpack import Screen, ScreenPack
from poc_studio.screens.kits import Kit

ROUTE = re.compile(r"^/(?:[a-z0-9]+(?:-[a-z0-9]+)*)?$")
MIN_PLAY = 3

_FORBIDDEN_TAGS = re.compile(
    r"<\s*/?\s*(script|iframe|object|embed|meta|base|form|link|style)\b", re.IGNORECASE
)
_TEMPLATE_TAG = re.compile(r"<\s*/?\s*template\b", re.IGNORECASE)
_URL_ATTRS = (
    "src", "href", "xlink:href", "srcset", "poster", "data", "action", "formaction", "background"
)  # fmt: skip
_STRIP = re.compile(r"[\s\x00-\x1f]+")
_SCHEME = re.compile(r"^(?:[a-z][a-z0-9+.\-]*:|//)", re.IGNORECASE)
_SRCSET_EXTERNAL = re.compile(r"(?:^|,)(?:https?:|//)", re.IGNORECASE)
_SCRIPT_BANNED: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (name, re.compile(pattern))
    for name, pattern in (
        ("fetch(", r"\bfetch\s*\("),
        ("XMLHttpRequest", r"\bXMLHttpRequest\b"),
        ("WebSocket", r"\bWebSocket\b"),
        ("EventSource", r"\bEventSource\b"),
        ("import(", r"\bimport\s*\("),
        ("importScripts", r"\bimportScripts\b"),
        ("sendBeacon", r"\bsendBeacon\b"),
        ("location assignment", r"\blocation\s*(?:=(?!=)|\.\s*\w+\s*=(?!=)|\.\s*(?:assign|replace)\s*\()"),
        ("eval(", r"\beval\s*\("),
        ("Function(", r"\bFunction\s*\("),
        ("cookie", r"\bcookie\b"),
        ("localStorage", r"\blocalStorage\b"),
        ("an http(s) URL", r"https?:\s*//"),
    )
)  # fmt: skip
_CSS_URL_EXTERNAL = re.compile(r"url\(\s*['\"]?\s*(?:https?:|//|javascript:)", re.IGNORECASE)
_CSS_DATA_URL = re.compile(
    r"url\(\s*(['\"])\s*data:.*?\1\s*\)|url\(\s*data:[^)]*\)", re.IGNORECASE | re.DOTALL
)
_BARE_URL = re.compile(r"https?:\s*//", re.IGNORECASE)
_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
_ANY_URL = re.compile(r"url\([^)]*\)")
_CLASS = re.compile(r"\.([A-Za-z_][\w-]*)")


class Issue(BaseModel):
    screen_id: str | None  # None for a pack-level issue
    code: str
    message: str

    def __str__(self) -> str:
        where = f" ({self.screen_id})" if self.screen_id else ""
        return f"[{self.code}]{where} {self.message}"


def _issue(screen_id: str | None, code: str, message: str) -> Issue:
    return Issue(screen_id=screen_id, code=code, message=message)


def _rules(css: str) -> list[tuple[str, tuple[str, ...]]]:
    """(prelude, enclosing at-rule names) for every block; '' marks an enclosing plain rule."""
    css = _ANY_URL.sub("url()", _COMMENT.sub("", css))
    out: list[tuple[str, tuple[str, ...]]] = []
    stack: list[str] = []
    buf: list[str] = []
    for ch in css:
        if ch == "{":
            prelude = "".join(buf).strip()
            buf.clear()
            out.append((prelude, tuple(stack)))
            stack.append(prelude.split()[0].lower() if prelude.startswith("@") else "")
        elif ch in "};":
            buf.clear()
            if ch == "}" and stack:
                stack.pop()
        else:
            buf.append(ch)
    return out


def _is_keyframes(name: str) -> bool:
    return name.startswith("@") and name.endswith("keyframes")


def _selectors(prelude: str) -> list[str]:
    return [s.strip() for s in prelude.split(",") if s.strip()]


def _css_url_issues(where: str, css: str, screen_id: str | None) -> list[Issue]:
    found: list[str] = []
    if _CSS_URL_EXTERNAL.search(css):
        found.append("a url() that loads an external or javascript: target")
    if re.search(r"@import\b", css, re.IGNORECASE):
        found.append("@import")
    if re.search(r"@font-face\b", css, re.IGNORECASE):
        found.append("@font-face")
    if _BARE_URL.search(_CSS_DATA_URL.sub("url()", css)):
        found.append("an http(s) URL")
    return [_issue(screen_id, "css_external", f"{where} holds {f}") for f in found]


def _product_css_issues(css: str, app_class: str) -> list[Issue]:
    prefix = f".pf .{app_class}"
    issues: list[Issue] = []
    for prelude, stack in _rules(css):
        if any(_is_keyframes(s) for s in stack):
            continue  # keyframe steps (from, 50%) are not selectors
        if prelude.startswith("@"):
            name = prelude.split()[0].lower()
            if name in ("@media", "@supports"):
                continue
            if _is_keyframes(name):
                kf = prelude.split(None, 1)[1] if " " in prelude else ""
                if not kf.startswith(app_class + "-"):
                    issues.append(
                        _issue(None, "css_scope", f"keyframes {kf!r} must start with '{app_class}-'")
                    )
            else:
                issues.append(_issue(None, "css_scope", f"at-rule {name} is not allowed in product_css"))
            continue
        for sel in _selectors(prelude):
            if not (
                sel == prefix or sel.startswith((prefix + " ", prefix + ".", prefix + ":", prefix + "["))
            ):
                issues.append(_issue(None, "css_scope", f"rule {sel!r} is not scoped under '{prefix}'"))
    return issues


def _step_css_issues(screen: Screen) -> list[Issue]:
    prefix = f".pf.sl-{screen.id}[data-step="
    issues: list[Issue] = []
    for prelude, stack in _rules(screen.step_css):
        if any(_is_keyframes(s) for s in stack):
            continue
        if prelude.startswith("@"):
            name = prelude.split()[0].lower()
            if name not in ("@media", "@supports"):
                issues.append(
                    _issue(screen.id, "step_css_scope", f"at-rule {name} is not allowed in step_css")
                )
            continue
        for sel in _selectors(prelude):
            if not sel.startswith(prefix):
                issues.append(_issue(screen.id, "step_css_scope", f"rule {sel!r} must start with '{prefix}'"))
    return issues


def _url_problem(attr: str, value: str) -> str | None:
    squashed = _STRIP.sub("", value)
    if attr == "srcset":
        return (
            "an external srcset"
            if _SRCSET_EXTERNAL.search(squashed) or "javascript:" in squashed.lower()
            else None
        )
    if squashed.lower().startswith("data:"):
        return None
    if squashed.lower().startswith("javascript:"):
        return "a javascript: URL"
    if _SCHEME.match(squashed):
        return "an external URL"
    return None


def _html_issues(screen: Screen, app_class: str, defined: set[str]) -> list[Issue]:
    sid = screen.id
    issues: list[Issue] = []
    if (tag := _FORBIDDEN_TAGS.search(screen.html)) is not None:
        issues.append(_issue(sid, "forbidden_element", f"<{tag.group(1).lower()}> elements are not allowed"))
    if _TEMPLATE_TAG.search(screen.html):
        issues.append(_issue(sid, "forbidden_element", "<template> tags are not allowed"))
    try:
        root = lxml_html.fromstring(f"<div>{screen.html}</div>")
    except Exception as exc:  # lxml raises several error types for broken markup
        return [*issues, _issue(sid, "html_parse", f"html does not parse: {exc}")]
    tops = [el for el in root if isinstance(el.tag, str)]
    if not tops:
        issues.append(_issue(sid, "root_class", f"screen html has no root element with class '{app_class}'"))
    for el in tops:
        if app_class not in (el.get("class") or "").split():
            issues.append(_issue(sid, "root_class", f"root <{el.tag}> must have class '{app_class}'"))
    used: set[str] = set()
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        used.update((el.get("class") or "").split())
        for name, value in el.attrib.items():
            lname = name.lower()
            if lname.startswith("on"):
                issues.append(_issue(sid, "forbidden_attribute", f"event handler {lname}= on <{el.tag}>"))
            elif lname == "srcdoc":
                issues.append(_issue(sid, "forbidden_attribute", f"<{el.tag} srcdoc=...> embeds a document"))
            elif lname in _URL_ATTRS:
                if (problem := _url_problem(lname, value)) is not None:
                    issues.append(_issue(sid, "external_url", f"<{el.tag} {lname}=...> is {problem}"))
            elif "javascript:" in _STRIP.sub("", value).lower():
                issues.append(_issue(sid, "external_url", f"<{el.tag} {lname}=...> holds a javascript: URL"))
    if undefined := sorted(used - defined):
        issues.append(
            _issue(sid, "undefined_class", f"classes not defined in the CSS: {', '.join(undefined)}")
        )
    return issues


def _script_issues(screen: Screen) -> list[Issue]:
    if not screen.script:
        return []
    return [
        _issue(screen.id, "script_network", f"script uses {name}, which is not allowed")
        for name, pattern in _SCRIPT_BANNED
        if pattern.search(screen.script)
    ]


def _anchor_issues(screen: Screen) -> list[Issue]:
    seen: set[str] = set()
    issues: list[Issue] = []
    for a in screen.anchors:
        key = " ".join(a.selector.split())
        if key in seen:
            issues.append(_issue(screen.id, "duplicate_anchor", f"anchor {a.selector!r} is listed twice"))
        seen.add(key)
    return issues


def _routing_issues(pack: ScreenPack) -> list[Issue]:
    issues: list[Issue] = []
    seen: set[str] = set()
    for s in pack.screens:
        if not ROUTE.fullmatch(s.route):
            issues.append(
                _issue(s.id, "route_format", f"route {s.route!r} must be '/' or '/' plus a kebab-case slug")
            )
        if s.route in seen:
            issues.append(_issue(s.id, "route_duplicate", f"route {s.route!r} is used by another screen"))
        seen.add(s.route)
    homes = [s.id for s in pack.screens if s.route == "/"]
    if len(homes) != 1:
        issues.append(
            _issue(None, "route_home", f"exactly one screen must have route '/', found {len(homes)}")
        )
    if (play := sum(1 for s in pack.screens if s.play)) < MIN_PLAY:
        issues.append(_issue(None, "play_count", f"at least {MIN_PLAY} screens need play=true, found {play}"))
    return issues


def _defined_classes(*sheets: str) -> set[str]:
    out: set[str] = set()
    for css in sheets:
        out.update(_CLASS.findall(_ANY_URL.sub("url()", _COMMENT.sub("", css))))
    return out


def validate(pack: ScreenPack, kit: Kit) -> list[Issue]:
    issues: list[Issue] = []
    if pack.app_class != kit.app_class:
        issues.append(_issue(None, "app_class", f"app_class {pack.app_class!r} must be {kit.app_class!r}"))
    issues += _product_css_issues(pack.product_css, kit.app_class)
    issues += _css_url_issues("product_css", pack.product_css, None)
    defined = _defined_classes(pack.product_css, kit.product_css, kit.icons_css)
    for s in pack.screens:
        issues += _step_css_issues(s)
        issues += _css_url_issues("step_css", s.step_css, s.id)
        issues += _html_issues(s, kit.app_class, defined)
        issues += _script_issues(s)
        issues += _anchor_issues(s)
    return issues + _routing_issues(pack)
