"""ScreenPack contract (spec 7b). The single source of the product screens."""

from typing import Annotated, Self

from lxml import html
from lxml.cssselect import CSSSelector
from lxml.etree import XPathError
from pydantic import BaseModel, Field, model_validator

SLUG = r"^[a-z0-9]+(-[a-z0-9]+)*$"
HEX = r"^#[0-9a-fA-F]{6}$"


class Anchor(BaseModel):
    selector: str = Field(min_length=1)  # must match >= 1 element in the owning screen's html
    purpose: str


class Screen(BaseModel):
    id: Annotated[str, Field(pattern=SLUG)]
    label: str
    route: str
    html: str
    step_css: str  # only .pf.sl-<id>[data-step] rules
    script: str | None = None  # window.__dkScripts body
    anchors: Annotated[list[Anchor], Field(min_length=3, max_length=8)]
    play: bool = False

    @model_validator(mode="after")
    def _anchors_match_html(self) -> Self:
        root = html.fromstring(f"<div>{self.html}</div>")
        for a in self.anchors:
            try:
                found = CSSSelector(a.selector)(root)
            except (XPathError, SyntaxError, ValueError) as exc:
                raise ValueError(f"screen {self.id}: invalid selector {a.selector!r}") from exc
            if not found:
                raise ValueError(f"screen {self.id}: anchor {a.selector!r} matches no element")
        return self


class ScreenPack(BaseModel):
    app_class: Annotated[str, Field(pattern=r"^[a-z][a-z0-9_-]*$")]
    accent: Annotated[str, Field(pattern=HEX)]
    product_css: str  # scoped under .pf .<app_class>
    screens: Annotated[list[Screen], Field(min_length=6, max_length=12)]

    @model_validator(mode="after")
    def _unique_ids(self) -> Self:
        ids = [s.id for s in self.screens]
        if len(set(ids)) != len(ids):
            raise ValueError("screen ids must be unique")
        return self
