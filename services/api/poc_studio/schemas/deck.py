"""DeckPlan: the #dk-data JSON of spec 7a plus the docs text. JSON keys are camelCase as in the deck."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator
from pydantic.alias_generators import to_camel

from poc_studio.schemas.screenpack import HEX

SlideKind = Literal["welcome", "overview", "area", "play", "close"]


class _Camel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)


class Step(_Camel):
    title: str
    caption: str
    spotlight: str  # must be one of the ScreenPack anchors[].selector values (checked in QA)


class Figure(_Camel):
    label: str
    value: float
    source: str
    verified: bool = False


class Slide(_Camel):
    id: str
    kind: SlideKind
    eyebrow: str | None = None
    title: str
    caption: str
    hint: str | None = None
    steps: list[Step] = []
    figures: list[Figure] = []

    @model_validator(mode="after")
    def _kind_rules(self) -> Self:
        if self.kind == "area" and not 3 <= len(self.steps) <= 5:
            raise ValueError(f"area slide {self.id} needs 3 to 5 steps, got {len(self.steps)}")
        if self.kind in ("welcome", "play", "close") and self.steps:
            raise ValueError(f"{self.kind} slide {self.id} takes no steps")
        if self.kind != "close" and self.figures:
            raise ValueError(f"only the close slide carries figures ({self.id})")
        return self


class PlayScreen(_Camel):
    id: str
    label: str


class DeckPlan(_Camel):
    title: str
    accent: Annotated[str, Field(pattern=HEX)]
    accent_ink: str = "#ffffff"
    logo: str = ""
    data_note: str = "Sample data: illustrative"
    byline: str = ""
    product_dark: bool = False
    play_screens: list[PlayScreen] = []
    slides: Annotated[list[Slide], Field(min_length=9, max_length=12)]
    exec_summary_md: str = ""
    user_flows_md: str = ""

    @model_validator(mode="after")
    def _structure(self) -> Self:
        kinds = [s.kind for s in self.slides]
        if kinds[0] != "welcome" or kinds[-1] != "close":
            raise ValueError("deck must start with welcome and end with close")
        if any(kinds.count(k) != 1 for k in ("welcome", "play", "close")):
            raise ValueError("deck needs exactly one welcome, one play and one close slide")
        if kinds.count("overview") > 1:
            raise ValueError("at most one overview slide")
        ids = [s.id for s in self.slides]
        if len(set(ids)) != len(ids):
            raise ValueError("slide ids must be unique")
        return self
