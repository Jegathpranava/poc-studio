"""Turn txt, vtt, md, docx and pdf files into a Transcript."""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Iterable
from pathlib import Path

from poc_studio.ingest.models import Segment, Transcript
from poc_studio.ingest.vtt import parse_timestamp, parse_vtt, split_speaker

MAX_FILE_BYTES = 20 * 1024 * 1024
SUPPORTED = (".txt", ".vtt", ".md", ".docx", ".pdf")

_TS_LINE = re.compile(
    r"^\s*[\[(]?(?P<ts>(?:\d+:)?\d{1,2}:\d{2}(?::\d{2})?(?:[.,]\d{1,3})?)[\])]?\s*[-–]?\s*(?P<rest>.*)$"
)


class FileTooLarge(ValueError):
    """Input file exceeds the 20 MB limit."""


class UnsupportedFile(ValueError):
    """Input file extension is not supported."""


def _read_text(path: Path) -> str:
    return path.read_bytes().decode("utf-8-sig", errors="replace")


def _paragraph_segments(text: str) -> list[Segment]:
    return [
        Segment(text=" ".join(p.split()))
        for p in re.split(r"\n\s*\n", text.replace("\r\n", "\n"))
        if p.strip()
    ]


def _line_segment(line: str) -> Segment | None:
    line = line.strip()
    if not line:
        return None
    ts: float | None = None
    m = _TS_LINE.match(line)
    if m and m.group("rest"):
        ts = parse_timestamp(m.group("ts"))
        line = m.group("rest").strip()
    speaker, text = split_speaker(line)
    if ts is None and speaker is None:
        return None
    return Segment(ts=ts, speaker=speaker, text=text)


def _parse_plain(text: str) -> list[Segment]:
    """Speaker/timestamp lines become segments; otherwise fall back to paragraphs."""
    text = text.replace("\r\n", "\n")
    lines = [ln for ln in text.split("\n") if ln.strip()]
    parsed = [_line_segment(ln) for ln in lines]
    if lines and sum(p is not None for p in parsed) >= max(2, len(lines) // 2):
        segments: list[Segment] = []
        for line, seg in zip(lines, parsed, strict=True):
            if seg is not None:
                segments.append(seg)
            elif segments:  # continuation of the previous utterance
                segments[-1].text += " " + line.strip()
            else:
                segments.append(Segment(text=line.strip()))
        return segments
    return _paragraph_segments(text)


def _parse_txt(path: Path) -> list[Segment]:
    return _parse_plain(_read_text(path))


def _parse_vtt_file(path: Path) -> list[Segment]:
    return parse_vtt(_read_text(path))


def _parse_docx(path: Path) -> list[Segment]:
    from docx import Document

    doc = Document(str(path))
    texts = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                t = cell.text.strip()
                if t:
                    texts.append(t)
    return _parse_plain("\n\n".join(texts))


def _parse_pdf(path: Path) -> list[Segment]:
    from pypdf import PdfReader

    segments: list[Segment] = []
    for page in PdfReader(str(path)).pages:
        text = page.extract_text() or ""
        segments.extend(_paragraph_segments(text))
    return segments


_PARSERS: dict[str, Callable[[Path], list[Segment]]] = {
    ".txt": _parse_txt,
    ".md": _parse_txt,
    ".vtt": _parse_vtt_file,
    ".docx": _parse_docx,
    ".pdf": _parse_pdf,
}


def parse_file(path: str | os.PathLike[str]) -> Transcript:
    p = Path(path)
    ext = p.suffix.lower()
    if ext not in _PARSERS:
        raise UnsupportedFile(f"Unsupported file type '{ext}'. Use one of: {', '.join(SUPPORTED)}")
    if os.path.getsize(p) > MAX_FILE_BYTES:
        raise FileTooLarge(f"{p.name} is larger than 20 MB")
    return Transcript.from_segments(_PARSERS[ext](p), [p.name])


def parse_files(paths: Iterable[str | os.PathLike[str]]) -> Transcript:
    segments: list[Segment] = []
    names: list[str] = []
    for path in paths:
        t = parse_file(path)
        segments.extend(t.segments)
        names.extend(t.source_files)
    return Transcript.from_segments(segments, names)
