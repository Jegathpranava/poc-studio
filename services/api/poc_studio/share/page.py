"""The self-contained summary page of the share zip (the `#share` layout of the approved design).

Everything is inline: the CSS (the design tokens), no scripts, no external URLs. The video and the deck are
relative links, so the page works from the unzipped folder.
"""

import re
from datetime import datetime
from html import escape
from pathlib import Path

from poc_studio.config import REPO_ROOT
from poc_studio.safety import CSS_URL_EXTERNAL, URL_ATTRS, url_problem
from poc_studio.share.content import ShareContent

SHARED_BY = "Skyform"
TOKENS_CSS = REPO_ROOT / "apps" / "web" / "app" / "tokens.css"
FALLBACK_TOKENS = (
    ":root{--color-bg:#F7F8FA;--color-surface:#FFFFFF;--color-fg:#0F1419;--color-muted:#3F4856;"
    "--color-border:#E1E5EA;--color-primary:#0F766E;--color-code-bg:#0F1419;--space-2:8px;--space-3:12px;"
    "--space-4:16px;--space-6:24px;--space-8:32px;--radius-md:6px;--radius-lg:10px;"
    '--font-body:ui-sans-serif,system-ui,"Segoe UI",sans-serif;--text-xs:0.75rem;--text-sm:0.8125rem;'
    "--text-base:0.9375rem;--text-lg:1.125rem;--text-xl:1.5rem}"
)
PAGE_CSS = """
*{box-sizing:border-box}body{margin:0;background:var(--color-bg);color:var(--color-fg);
font-family:var(--font-body);font-size:var(--text-base);line-height:1.5}
.share{max-width:760px;margin:0 auto;padding:var(--space-8) var(--space-4)}
.share h1{font-size:var(--text-xl);line-height:1.2;margin:var(--space-2) 0}
.share h2{font-size:var(--text-lg);margin:0 0 var(--space-2)}
.muted{color:var(--color-muted)}.xs{font-size:var(--text-xs)}
.stack{display:flex;flex-direction:column;gap:var(--space-4);margin-top:var(--space-6)}
.player,.poster{width:100%;aspect-ratio:16/9;background:var(--color-code-bg);border-radius:var(--radius-md);display:block}
.poster{display:flex;align-items:center;justify-content:center;color:var(--color-surface);text-align:center;padding:var(--space-4)}
.item{display:block;padding:var(--space-3) var(--space-4);border:1px solid var(--color-border);
border-radius:var(--radius-lg);background:var(--color-surface);color:var(--color-fg);text-decoration:none}
.item b{display:block}.panel{background:var(--color-surface);border:1px solid var(--color-border);
border-radius:var(--radius-lg);padding:var(--space-4)}
ul{margin:0;padding-left:var(--space-4)}li{margin:var(--space-2) 0}
footer{margin-top:var(--space-8);padding-top:var(--space-4);border-top:1px solid var(--color-border)}
"""


def _tokens() -> str:
    try:
        css = TOKENS_CSS.read_text(encoding="utf-8")
    except OSError:
        return FALLBACK_TOKENS
    # `rgb(15 20 25 / 0.14)` reads as a phone number to the PII scan and the page uses none of them.
    return re.sub(r"--[\w-]+:\s*rgb\([^;]*;", "", css)


def render_index(content: ShareContent, expires: datetime, *, pdf: bool = False) -> str:
    """`pdf=True` swaps the video for a poster note and drops the deck link (a PDF cannot play either)."""
    e = escape
    media = ""
    if content.has_video:
        media = (
            '<div class="poster">Walkthrough video: see walkthrough.mp4 in the share folder.</div>'
            if pdf
            else '<video class="player" controls preload="metadata" playsinline>'
            '<source src="walkthrough.mp4" type="video/mp4">Your browser cannot play MP4 here.</video>'
        )
    deck = ""
    if content.has_deck and not pdf:
        deck = (
            '<a class="item" href="deck.html"><b>Open the interactive deck</b>'
            '<span class="xs muted">Click through each screen, step by step</span></a>'
        )
    points = "".join(f"<li>{e(p)}</li>" for p in content.pain_points)
    heard = f'<div class="panel"><h2>What we heard</h2><ul>{points}</ul></div>' if points else ""
    pilot = f'<p class="xs muted">{e(content.pilot)}</p>' if content.pilot else ""
    date = f"{expires.day} {expires:%B %Y}"
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        f"<title>{e(content.title)}</title><style>{_tokens()}{PAGE_CSS}</style></head><body>"
        '<div class="share"><header><div class="xs muted">'
        f"Prepared for {e(content.client)} by {SHARED_BY}</div>"
        f'<h1>{e(content.title)}</h1><p class="muted">{e(content.summary)}</p></header>'
        f'<div class="stack">{media}{deck}{heard}{pilot}</div>'
        '<footer class="xs muted">'
        f"Shared by {SHARED_BY}. This page is read-only and expires on {date}.</footer>"
        "</div></body></html>"
    )


_ATTR = re.compile(r"""\b([a-zA-Z][\w:-]*)\s*=\s*(?:"([^"]*)"|'([^']*)')""")


def external_refs(html: str) -> list[str]:
    """Why the page points outside itself (attribute URLs, CSS `url()`), by the shared deck rules."""
    problems: list[str] = []
    for m in _ATTR.finditer(html):
        attr = m.group(1).lower()
        if attr in URL_ATTRS and (why := url_problem(attr, m.group(2) or m.group(3) or "")):
            problems.append(f"{attr}: {why}")
    if CSS_URL_EXTERNAL.search(html):
        problems.append("css: an external url()")
    return problems


def write_pdf(html: str, out: Path) -> None:
    """Render `html` to an A4 PDF with Playwright Chromium."""
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        try:
            page = browser.new_page()
            page.set_content(html, wait_until="load")
            page.pdf(path=str(out), format="A4", print_background=True)
        finally:
            browser.close()
