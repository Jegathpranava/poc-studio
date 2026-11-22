"""Self-containment rules shared by the ScreenPack validator and the deck assembler.

The validator reports these as issues so a bad pack goes back to the model; the assembler raises on the same
patterns as the last line of defence. Keeping one copy stops the two from drifting apart.

One deliberate difference stays outside this module: the validator also forbids `<style>` in screen HTML
(screens carry no inline style blocks; their CSS lives in `product_css` and `step_css`), while the assembler
emits its own `<style>` element and so cannot ban the tag.
"""

import posixpath
import re

URL_ATTRS = (
    "src", "href", "xlink:href", "srcset", "poster", "data", "action", "formaction", "srcdoc", "background"
)  # fmt: skip
FORBIDDEN_TAGS = re.compile(r"<\s*/?\s*(script|iframe|object|embed|meta|base|form|link)\b", re.IGNORECASE)
TEMPLATE_TAG = re.compile(r"<\s*/?\s*template\b", re.IGNORECASE)
STRIP = re.compile(r"[\s\x00-\x1f]+")
SCHEME = re.compile(r"^(?:[a-z][a-z0-9+.\-]*:|//)", re.IGNORECASE)
SRCSET_EXTERNAL = re.compile(r"(?:^|,)(?:https?:|//)", re.IGNORECASE)
SCRIPT_BANNED: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (name, re.compile(pattern))
    for name, pattern in (
        ("fetch(", r"\bfetch\s*\("),
        ("XMLHttpRequest", r"\bXMLHttpRequest\b"),
        ("WebSocket", r"\bWebSocket\b"),
        ("EventSource", r"\bEventSource\b"),
        ("import(", r"\bimport\s*\("),
        ("importScripts", r"\bimportScripts\b"),
        ("navigator.sendBeacon", r"\bsendBeacon\b"),
        ("location assignment", r"\blocation\s*(?:=(?!=)|\.\s*\w+\s*=(?!=)|\.\s*(?:assign|replace)\s*\()"),
        ("eval(", r"\beval\s*\("),
        ("Function(", r"\bFunction\s*\("),
        ("document.cookie", r"\bcookie\b"),
        ("localStorage", r"\blocalStorage\b"),
        ("an http(s) URL", r"https?:\s*//"),
    )
)  # fmt: skip
CSS_URL_EXTERNAL = re.compile(r"url\(\s*['\"]?\s*(?:https?:|//|javascript:)", re.IGNORECASE)
CSS_IMAGE_SET = re.compile(r"image-set\(\s*['\"]\s*(?:https?:|//|javascript:)", re.IGNORECASE)
CSS_DATA_URL = re.compile(
    r"url\(\s*(['\"])\s*data:.*?\1\s*\)|url\(\s*data:[^)]*\)", re.IGNORECASE | re.DOTALL
)
BARE_URL = re.compile(r"https?:\s*//", re.IGNORECASE)


def url_problem(attr: str, value: str) -> str | None:
    """Why a URL attribute value points outside the file, or None."""
    squashed = STRIP.sub("", value)
    if attr == "srcset":
        return (
            "an external srcset"
            if SRCSET_EXTERNAL.search(squashed) or "javascript:" in squashed.lower()
            else None
        )
    if squashed.lower().startswith("data:"):
        return None
    if squashed.lower().startswith("javascript:"):
        return "a javascript: URL"
    if SCHEME.match(squashed):
        return "an external URL"
    return None


# Node and system access in code the model wrote into the generated Next.js app (the sandbox fix path).
_NODE_MODULES = r"(?:node:[\w/.\-]+|(?:fs|child_process|net|http|https|os|worker_threads|vm)(?:/[\w/.\-]*)?)"
NODE_BANNED: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (name, re.compile(pattern))
    for name, pattern in (
        ("require(", r"\brequire\s*\("),
        ("import(", r"\bimport\s*\("),
        ("a node or system module import", rf"""(?:\bfrom\s*|\bimport\s*)(['"]){_NODE_MODULES}\1"""),
        ("process.env", r"\bprocess\s*\.\s*env\b"),
        ("process.binding", r"\bprocess\s*\.\s*binding\b"),
        ("eval(", r"\beval\s*\("),
        ("new Function(", r"\bnew\s+Function\s*\("),
        ("fetch( with an absolute URL", r"""\bfetch\s*\(\s*[`'"]\s*(?:[a-z][a-z0-9+.\-]*:|//)"""),
        ("XMLHttpRequest", r"\bXMLHttpRequest\b"),
        ("WebSocket", r"\bWebSocket\b"),
    )
)  # fmt: skip
_IMPORT_SPECIFIER = re.compile(r"""(?:\bfrom\s*|\bimport\s*|\brequire\s*\(\s*)(['"])([^'"\n]+)\1""")
_FIX_ROOTS = ("app", "components")


def node_access_problem(path: str, content: str) -> str | None:
    """Why `content` (the text of the app file at `path`) reaches for node or system access, or None.

    Relative imports must stay inside `app/` or `components/`."""
    for name, pattern in NODE_BANNED:
        if pattern.search(content):
            return f"uses {name}"
    folder = posixpath.dirname(path)
    for match in _IMPORT_SPECIFIER.finditer(content):
        spec = match.group(2)
        if spec.startswith("."):
            target = posixpath.normpath(posixpath.join(folder, spec))
            if target.split("/")[0] not in _FIX_ROOTS:
                return f"imports {spec!r}, which leaves app/ and components/"
    return None
