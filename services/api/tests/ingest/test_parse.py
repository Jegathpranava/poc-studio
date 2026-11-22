from pathlib import Path

import pytest

from poc_studio.ingest import FileTooLarge, UnsupportedFile, parse_file, parse_files
from poc_studio.ingest.vtt import parse_vtt

FIX = Path(__file__).parent / "fixtures"


def _close(actual: int, expected: int) -> bool:
    return abs(actual - expected) <= max(0.02 * expected, 0)


def test_txt_keeps_speakers_timestamps_and_bom_handling() -> None:
    t = parse_file(FIX / "sample.txt")
    assert t.source_files == ["sample.txt"]
    assert t.segments[0].speaker == "Alice Smith"
    assert t.segments[0].ts == 5.0
    assert t.segments[1].ts == 12.0
    assert "continues the thought" in t.segments[1].text  # continuation line merged
    assert not t.segments[0].text.startswith("﻿")
    assert _close(t.word_count, 19)


def test_vtt_keeps_speakers_and_timestamps() -> None:
    t = parse_file(FIX / "sample.vtt")
    assert [s.speaker for s in t.segments] == ["Alice Smith", "Bob Jones", None]
    assert [s.ts for s in t.segments] == [1.0, 3723.5, 10.25]
    assert t.segments[0].text == "We need a dashboard for weekly sales."  # tags stripped, cue joined
    assert all("NOTE" not in s.text for s in t.segments)
    assert _close(t.word_count, 18)


def test_vtt_comma_timings_and_empty_cue() -> None:
    segs = parse_vtt(
        "WEBVTT\n\n00:00:01,500 --> 00:00:02,000\n<c.yellow>Hi</c>\n\n00:00:03.000 --> 00:00:04.000\n\n"
    )
    assert len(segs) == 1 and segs[0].ts == 1.5 and segs[0].text == "Hi"


def test_md_paragraphs() -> None:
    t = parse_file(FIX / "sample.md")
    assert len(t.segments) == 3
    assert all(s.speaker is None and s.ts is None for s in t.segments)
    assert _close(t.word_count, 15)


def test_docx_includes_table_cells() -> None:
    t = parse_file(FIX / "sample.docx")
    text = " ".join(s.text for s in t.segments)
    assert "Owner Alice" in text and "Due Friday" in text
    assert _close(t.word_count, 15)


def test_pdf_extracts_text() -> None:
    t = parse_file(FIX / "sample.pdf")
    assert "dashboard for the weekly review" in " ".join(s.text for s in t.segments)
    assert _close(t.word_count, 13)


def test_file_over_20mb_raises(tmp_path: Path) -> None:
    big = tmp_path / "big.txt"
    with big.open("wb") as f:
        f.truncate(25 * 1024 * 1024)  # sparse file
    with pytest.raises(FileTooLarge):
        parse_file(big)


def test_parse_files_merges_in_order() -> None:
    t = parse_files([FIX / "sample.txt", FIX / "sample.md"])
    assert t.source_files == ["sample.txt", "sample.md"]
    expected = parse_file(FIX / "sample.txt").word_count + parse_file(FIX / "sample.md").word_count
    assert t.word_count == expected
    assert t.segments[0].speaker == "Alice Smith"


def test_unsupported_extension(tmp_path: Path) -> None:
    p = tmp_path / "sheet.xlsx"
    p.write_bytes(b"x")
    with pytest.raises(UnsupportedFile):
        parse_file(p)
