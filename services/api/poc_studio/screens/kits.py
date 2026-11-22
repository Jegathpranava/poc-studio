"""Sector kits (templates/<sector>/kit): the design system the Prototype Builder starts from."""

import json
import re
from dataclasses import dataclass
from pathlib import Path

TEMPLATES_DIR = Path(__file__).resolve().parents[4] / "templates"
DEFAULT_SECTOR = "logistics"

# Closest-kit hints for the sector "other" (and unknown sectors): word prefixes searched in the brief.
_KEYWORDS: dict[str, tuple[str, ...]] = {
    "logistics": (
        "shipment", "freight", "fleet", "deliver", "warehouse", "route", "driver", "supply", "depot", "cargo",
    ),
    "healthcare": ("patient", "clinic", "hospital", "appointment", "doctor", "nurse", "medical", "health"),
    "e-commerce": ("order", "cart", "checkout", "product", "store", "shop", "retail", "catalog", "merchant"),
    "fintech": ("payment", "bank", "loan", "invoice", "transaction", "ledger", "fraud", "credit", "billing"),
}  # fmt: skip


@dataclass(frozen=True)
class ExampleScreen:
    id: str
    label: str
    html: str
    anchors: tuple[str, ...]


@dataclass(frozen=True)
class Kit:
    sector: str
    app_class: str
    accent: str
    product_css: str
    icons_css: str
    selectors_md: str
    examples: tuple[ExampleScreen, ...]


def sector_dir(sector: str, text: str = "") -> str:
    """Directory name of the kit for a requirements sector; for "other", the closest kit by keyword."""
    index: dict[str, str] = json.loads((TEMPLATES_DIR / "sectors.json").read_text(encoding="utf-8"))
    if sector in index:
        return index[sector]
    words = re.findall(r"[a-z]+", text.lower())
    best, best_score = DEFAULT_SECTOR, 0
    for name, hints in _KEYWORDS.items():
        score = sum(1 for w in words if w.startswith(hints))
        if score > best_score:
            best, best_score = name, score
    return index.get(best, DEFAULT_SECTOR)


def load_kit(directory: str) -> Kit:
    kit = TEMPLATES_DIR / directory / "kit"
    meta = json.loads((kit / "kit.json").read_text(encoding="utf-8"))
    examples = tuple(
        ExampleScreen(
            id=s["id"],
            label=s["label"],
            html=(kit / s["file"]).read_text(encoding="utf-8"),
            anchors=tuple(s["anchors"]),
        )
        for s in meta["screens"]
    )
    return Kit(
        sector=meta["sector"],
        app_class=meta["app_class"],
        accent=meta["accent"],
        product_css=(kit / "product.css").read_text(encoding="utf-8"),
        icons_css=(kit / "icons.css").read_text(encoding="utf-8"),
        selectors_md=(kit / "selectors.md").read_text(encoding="utf-8"),
        examples=examples,
    )
