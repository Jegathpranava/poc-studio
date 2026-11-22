"""QA Reviewer checks (spec 7a and 7b). Pure functions over `QAInputs`; the agent loads the inputs.

Every check returns a `Check`. `report_only` means routing never sends the run back for it (a bug, a build
failure, PII, or an input that is simply missing). The MP4 check lives in `media/video.py` (`video_check`).
"""

import re
from dataclasses import dataclass, field
from typing import Any

from lxml import html as lxml_html
from lxml.cssselect import CSSSelector
from lxml.etree import XPathError
from pydantic import BaseModel

from poc_studio.qa.secrets import Finding
from poc_studio.safety import CSS_IMAGE_SET, CSS_URL_EXTERNAL, URL_ATTRS, url_problem
from poc_studio.schemas.architecture import Architecture
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.requirements import Requirements
from poc_studio.schemas.screenpack import ScreenPack

MATCH_SHARE = 0.6
STUB = "skipped (stub)"


class Check(BaseModel):
    name: str
    ok: bool
    detail: str
    owner_agent: str
    report_only: bool = False


@dataclass
class QAInputs:
    req: Requirements | None = None
    arch: Architecture | None = None
    pack: ScreenPack | None = None
    plan: DeckPlan | None = None
    deck_html: str | None = None
    deck_failed: bool = False  # pitch or assemble reported {"ok": False}: a real failure even in stub mode
    build: dict[str, Any] | None = None
    readme: str = ""
    secret_findings: list[Finding] = field(default_factory=list)
    pii_findings: list[Finding] = field(default_factory=list)
    lenient: bool = False  # POC_ALLOW_STUB_SKIP: a missing input is a skip, not a failure


def _ok(name: str, owner: str, detail: str = "ok") -> Check:
    return Check(name=name, ok=True, detail=detail, owner_agent=owner)


def _fail(name: str, owner: str, detail: str, report_only: bool = False) -> Check:
    return Check(name=name, ok=False, detail=detail[:500], owner_agent=owner, report_only=report_only)


def _missing(ins: QAInputs, name: str, owner: str, what: str) -> Check:
    if ins.lenient:
        return _ok(name, owner, STUB)
    return _fail(name, owner, f"missing input: {what}", report_only=True)


def _fragment(markup: str) -> Any:
    return lxml_html.fromstring(f"<div>{markup}</div>")


def _text(markup: str) -> str:
    return " ".join(_fragment(markup).text_content().split())


def deck_present(ins: QAInputs) -> Check:
    name, owner = "deck_present", "assemble"
    if ins.deck_html:
        return _ok(name, owner)
    if ins.lenient and not ins.deck_failed:
        return _ok(name, owner, STUB)
    return _fail(name, owner, "no deck HTML artifact was produced", report_only=True)


def _css_problems(css: str, where: str) -> list[str]:
    out: list[str] = []
    if CSS_URL_EXTERNAL.search(css):
        out.append(f"{where}: css url() loads an external target")
    if "@import" in css.lower():
        out.append(f"{where}: css @import")
    if CSS_IMAGE_SET.search(css):
        out.append(f"{where}: css image-set() loads an external target")
    return out


def deck_self_contained(ins: QAInputs) -> Check:
    """Re-parse the deck for anything that loads from outside the file (a bug: report, never send back)."""
    name, owner = "deck_self_contained", "assemble"
    if not ins.deck_html:
        return _ok(name, owner, "skipped, no deck" if ins.lenient or ins.deck_failed else "no deck to check")
    problems: list[str] = []
    root = lxml_html.fromstring(ins.deck_html)
    for el in root.iter():
        if not isinstance(el.tag, str):
            continue
        for attr in URL_ATTRS:
            value = el.get(attr)
            if value is not None and (problem := url_problem(attr, value)) is not None:
                problems.append(f"<{el.tag} {attr}> is {problem}")
        if style := el.get("style"):
            problems += _css_problems(style, f"<{el.tag} style>")
        if el.tag == "style":
            problems += _css_problems(el.text or "", "<style>")
    return _fail(name, owner, "; ".join(problems[:5]), report_only=True) if problems else _ok(name, owner)


def spotlights_resolve(ins: QAInputs) -> Check:
    name, owner = "spotlights_resolve", "pitch"
    if ins.plan is None or ins.pack is None:
        return _missing(ins, name, owner, "deck plan or screenpack")
    screens = {s.id: s for s in ins.pack.screens}
    bad: list[str] = []
    for slide in ins.plan.slides:
        if slide.kind not in ("overview", "area"):
            continue
        screen = screens.get(slide.id)
        if screen is None:
            bad.append(f"{slide.id}: no such screen")
            continue
        root = _fragment(screen.html)
        for step in slide.steps:
            try:
                found = CSSSelector(step.spotlight)(root)
            except (XPathError, SyntaxError, ValueError):
                found = []
            if not found:
                bad.append(f"{slide.id}: {step.spotlight!r}")
    return _fail(name, owner, "unresolved spotlight: " + "; ".join(bad[:5])) if bad else _ok(name, owner)


def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9]+", text.lower()) if len(w) > 3]


def loose_match(feature: str, haystack: str) -> bool:
    """At least 60% of the feature name's words longer than 3 characters appear in the text."""
    words = _words(feature)
    low = haystack.lower()
    if not words:
        return feature.lower().strip() in low
    return sum(w in low for w in words) / len(words) >= MATCH_SHARE


def _deck_text(plan: DeckPlan) -> str:
    parts: list[str] = [plan.title]
    for s in plan.slides:
        parts += [s.title, s.caption, s.hint or "", s.eyebrow or ""]
        parts += [t for st in s.steps for t in (st.title, st.caption)]
    return " ".join(parts)


def features_consistent(ins: QAInputs) -> Check:
    name = "features_consistent"
    if ins.req is None or ins.pack is None:
        return _missing(ins, name, "screens", "requirements or screenpack")
    screens_text = " ".join(f"{s.label} {_text(s.html)}" for s in ins.pack.screens)
    deck_text = f"{_deck_text(ins.plan)} {ins.readme}" if ins.plan is not None else None
    for feature in (f for f in ins.req.features if f.priority == "P1"):
        if not loose_match(feature.name, screens_text):
            return _fail(name, "screens", f"P1 feature not on any screen: {feature.name}")
        if deck_text is not None and not loose_match(feature.name, deck_text):
            return _fail(name, "pitch", f"P1 feature not in the deck or README: {feature.name}")
    return _ok(name, "pitch") if ins.plan is not None else _ok(name, "screens", "screens only, no deck plan")


def names_consistent(ins: QAInputs) -> Check:
    name, owner = "names_consistent", "pitch"
    if ins.req is None or ins.plan is None:
        return _missing(ins, name, owner, "requirements or deck plan")
    client = ins.req.client
    welcome = next((s for s in ins.plan.slides if s.kind == "welcome"), None)
    head = ins.plan.title
    if welcome is not None:
        head += f" {welcome.title} {welcome.caption} {welcome.eyebrow or ''}"
    problems = []
    if client not in head:
        problems.append(f"client {client!r} is not in the deck title or welcome slide")
    if client not in ins.plan.exec_summary_md:
        problems.append(f"client {client!r} is not in the executive summary")
    return _fail(name, owner, "; ".join(problems)) if problems else _ok(name, owner)


def _is_monthly_total(label: str, source: str) -> bool:
    if source.replace(" ", "").endswith("monthly_cost.total_usd"):
        return True
    low = label.lower()
    return "month" in low and any(w in low for w in ("total", "cost", "running"))


def _money_forms(value: float) -> list[str]:
    forms = [f"{value:,.2f}"]
    if abs(value - round(value)) < 0.005:
        forms.append(f"{round(value):,}")
    return forms


def costs_consistent(ins: QAInputs) -> Check:
    name, owner = "costs_consistent", "pitch"
    if ins.arch is None or ins.plan is None:
        return _missing(ins, name, owner, "architecture or deck plan")
    total = ins.arch.monthly_cost.total_usd
    problems = [
        f"close figure {f.label!r} is {f.value:g}, architecture says {total:g}"
        for s in ins.plan.slides if s.kind == "close"
        for f in s.figures
        if _is_monthly_total(f.label, f.source) and abs(f.value - total) > 0.01
    ]  # fmt: skip
    if not any(form in ins.plan.exec_summary_md for form in _money_forms(total)):
        problems.append(f"monthly total ${total:,.2f} is not in the executive summary")
    return _fail(name, owner, "; ".join(problems)) if problems else _ok(name, owner)


def figures_sourced(ins: QAInputs) -> Check:
    name, owner = "figures_sourced", "pitch"
    if ins.plan is None:
        return _missing(ins, name, owner, "deck plan")
    bad = [f.label for s in ins.plan.slides if s.kind == "close" for f in s.figures if not f.verified]
    if bad:
        return _fail(name, owner, "figure without a verified source: " + ", ".join(bad))
    return _ok(name, owner)


def build_passed(ins: QAInputs) -> Check:
    name, owner = "build_passed", "port"
    if ins.build is None:
        return _missing(ins, name, owner, "build.json")
    if ins.build.get("ok") is True:
        return _ok(name, owner)
    err = ins.build.get("error")
    message = err.get("message") if isinstance(err, dict) else err
    return _fail(name, owner, f"repo code did not build: {message or 'see build.json'}", report_only=True)


def no_secrets(ins: QAInputs) -> Check:
    name, owner = "no_secrets", "port"
    if not ins.secret_findings:
        return _ok(name, owner)
    shown = ", ".join(f"{f.file}:{f.line} {f.kind}" for f in ins.secret_findings[:5])
    return _fail(name, owner, f"{len(ins.secret_findings)} secret finding(s): {shown}")


def no_pii(ins: QAInputs) -> Check:
    name = "no_pii"
    if not ins.pii_findings:
        return _ok(name, "pitch")
    first = ins.pii_findings[0].file
    owner = "screens" if first.startswith("app/") else "pitch"
    shown = ", ".join(f"{f.file}:{f.line} {f.kind}" for f in ins.pii_findings[:5])
    return _fail(name, owner, f"warning, PII outside the allow-list: {shown}", report_only=True)


ALL_CHECKS = (
    deck_present, deck_self_contained, spotlights_resolve, features_consistent, names_consistent,
    costs_consistent, figures_sourced, build_passed, no_secrets, no_pii,
)  # fmt: skip


def run_checks(ins: QAInputs) -> list[Check]:
    return [check(ins) for check in ALL_CHECKS]
