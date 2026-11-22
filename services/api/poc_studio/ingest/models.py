from __future__ import annotations

from pydantic import BaseModel, Field


class Segment(BaseModel):
    ts: float | None = None  # seconds from start, when known
    speaker: str | None = None
    text: str


class Transcript(BaseModel):
    segments: list[Segment] = Field(default_factory=list)
    source_files: list[str] = Field(default_factory=list)
    word_count: int = 0

    @classmethod
    def from_segments(cls, segments: list[Segment], source_files: list[str]) -> Transcript:
        return cls(
            segments=segments,
            source_files=source_files,
            word_count=sum(len(s.text.split()) for s in segments),
        )
