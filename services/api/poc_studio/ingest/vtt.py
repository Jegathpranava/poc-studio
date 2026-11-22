"""Dependency-free WebVTT parser."""

from __future__ import annotations

import re

from poc_studio.ingest.models import Segment

_TIMING = re.compile(
    r"^\s*(?P<start>(?:\d+:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?)\s*-->\s*(?:\d+:)?\d{1,2}:\d{2}(?:[.,]\d{1,3})?"
)
_VOICE = re.compile(r"^<v(?:\.[^\s>]+)*\s+([^>]+)>", re.IGNORECASE)
_TAG = re.compile(r"</?[^>]+>")
_SPEAKER_PREFIX = re.compile(r"^([A-Z][\w.'-]*(?: [\w.'-]+){0,3}):\s+(\S.*)$")


def parse_timestamp(value: str) -> float:
    parts = value.replace(",", ".").split(":")
    seconds = 0.0
    for p in parts:
        seconds = seconds * 60 + float(p)
    return seconds


def split_speaker(line: str) -> tuple[str | None, str]:
    m = _SPEAKER_PREFIX.match(line)
    if m:
        return m.group(1).strip(), m.group(2).strip()
    return None, line.strip()


def parse_vtt(content: str) -> list[Segment]:
    content = content.lstrip("\ufeff").replace("\r\n", "\n").replace("\r", "\n")
    segments: list[Segment] = []
    for block in re.split(r"\n{2,}", content.strip()):
        lines = block.split("\n")
        if lines and lines[0].startswith("WEBVTT"):
            continue
        if lines and re.match(r"^(NOTE|STYLE|REGION)\b", lines[0]):
            continue
        idx = next((i for i, ln in enumerate(lines) if _TIMING.match(ln)), None)
        if idx is None:
            continue
        timing = _TIMING.match(lines[idx])
        assert timing is not None
        ts = parse_timestamp(timing.group("start"))
        speaker: str | None = None
        parts: list[str] = []
        for raw in lines[idx + 1 :]:
            voice = _VOICE.match(raw.strip())
            if voice and speaker is None:
                speaker = voice.group(1).strip()
            text = _TAG.sub("", raw).strip()
            if text:
                parts.append(text)
        if not parts:
            continue
        text = " ".join(parts)
        if speaker is None:
            speaker, text = split_speaker(text)
        if text:
            segments.append(Segment(ts=ts, speaker=speaker, text=text))
    return segments
