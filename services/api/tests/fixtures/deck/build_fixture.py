"""Regenerates pack.json, plan.json and icons.css from templates/logistics/kit (run from services/api)."""

import json
import re
from pathlib import Path

from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.screenpack import Screen, ScreenPack

ROOT = Path(__file__).resolve().parents[5]
KIT = ROOT / "templates" / "logistics" / "kit"
OUT = Path(__file__).parent

# (id, label, kit screen file, title swap)
SCREENS = [
    ("dashboard", "Dashboard", "dashboard", None),
    ("shipments", "Shipments list and detail", "list-detail", None),
    ("create-shipment", "Create shipment", "form", None),
    ("fleet", "Fleet overview", "dashboard", ("Operations overview", "Fleet overview")),
    ("routes", "Route board", "list-detail", None),
    ("new-route", "Plan a route", "form", ("Create shipment", "Plan a route")),
]


def anchors_of(fragment: str) -> list[dict[str, str]]:
    names = sorted(set(re.findall(r'data-anchor="([^"]+)"', fragment)))
    return [{"selector": f'[data-anchor="{n}"]', "purpose": n.replace("-", " ")} for n in names][:8]


def step_css(sid: str) -> str:
    return f'.pf.sl-{sid}[data-step="1"] .lgx [data-anchor="nav-active"]{{outline-offset:2px}}'


def build_pack() -> ScreenPack:
    screens = []
    for sid, label, src, swap in SCREENS:
        fragment = (KIT / "screens" / f"{src}.html").read_text(encoding="utf-8")
        if swap:
            fragment = fragment.replace(*swap)
        screens.append(
            Screen(id=sid, label=label, route=f"/{sid}", html=fragment, step_css=step_css(sid),
                   anchors=anchors_of(fragment), play=sid in ("dashboard", "shipments", "create-shipment"))
        )
    return ScreenPack(app_class="lgx", accent="#b45309",
                      product_css=(KIT / "product.css").read_text(encoding="utf-8"), screens=screens)


def build_plan(pack: ScreenPack) -> DeckPlan:
    def steps(sid: str, n: int) -> list[dict[str, str]]:
        sel = [a.selector for a in next(s for s in pack.screens if s.id == sid).anchors]
        return [{"title": f"Step {i + 1}", "caption": f"What this part of {sid} does.",
                 "spotlight": sel[i % len(sel)]} for i in range(n)]

    area = ["shipments", "create-shipment", "fleet", "routes", "new-route"]
    slides: list[dict] = [
        {"id": "welcome", "kind": "welcome", "eyebrow": "Northline Freight", "title": "Depot operations, one screen",
         "caption": "A guided tour of the proposed prototype."},
        {"id": "dashboard", "kind": "overview", "eyebrow": "Overview", "title": "The product at a glance",
         "caption": "Four moments from a shift.", "steps": steps("dashboard", 4)},
        *[{"id": s, "kind": "area", "eyebrow": "Area", "title": s.replace("-", " ").title(),
           "caption": f"How {s} works.", "steps": steps(s, 3)} for s in area],
        {"id": "play", "kind": "play", "title": "Your turn", "caption": "Click through the screens.",
         "hint": "Actions are simulated."},
        {"id": "close", "kind": "close", "title": "What it is worth",
         "caption": "Figures from the brief.", "figures": [
             {"label": "Late deliveries cut", "value": 30, "source": "brief: goals", "verified": True},
             {"label": "Dispatch hours saved per week", "value": 12, "source": "brief: pain points", "verified": True},
             {"label": "Pilot weeks", "value": 6, "source": "architecture: plan", "verified": True}]},
    ]
    return DeckPlan.model_validate({
        "title": "Northline Freight prototype", "accent": "#b45309", "byline": "Prepared by PoC Studio",
        "playScreens": [{"id": s.id, "label": s.label} for s in pack.screens if s.play], "slides": slides})


if __name__ == "__main__":
    pack = build_pack()
    plan = build_plan(pack)
    (OUT / "pack.json").write_text(pack.model_dump_json(indent=1), encoding="utf-8")
    (OUT / "plan.json").write_text(json.dumps(plan.model_dump(by_alias=True), indent=1), encoding="utf-8")
    (OUT / "icons.css").write_text((KIT / "icons.css").read_text(encoding="utf-8"), encoding="utf-8")
    print("ok", [(s.id, len(s.anchors)) for s in pack.screens])
