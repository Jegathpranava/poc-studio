"""Walkthrough recorder: plays the deck through `window.__deck` in headless Chromium and writes an MP4.

Playwright records WebM at 1280x720; the bundled ffmpeg (`imageio-ffmpeg`) converts it to H.264 MP4. Every
step of every slide except the hands-on (`play`) slide is held for 3 s plus 25 ms per caption character,
scaled so the whole video lands between 120 and 180 s (spec 13). Chapters come from the slide titles.
"""

import json
import re
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any

from pydantic import BaseModel

BASE_HOLD_S = 3.0
PER_CHAR_S = 0.025
MIN_TOTAL_S = 120.0
MAX_TOTAL_S = 180.0
READY_TIMEOUT_MS = 15_000
SIZE = (1280, 720)


class VideoError(RuntimeError):
    pass


class Chapter(BaseModel):
    t: float
    title: str


class VideoResult(BaseModel):
    path: Path
    duration_s: float
    chapters: list[Chapter]


def plan_holds(caption_lengths: list[int], hold_s: float | None = None) -> list[float]:
    """Seconds to hold each step. A fixed `hold_s` (tests) wins; otherwise 3 s + 25 ms per character, scaled
    only when the total falls outside 120 to 180 s."""
    if hold_s is not None:
        return [hold_s] * len(caption_lengths)
    raw = [BASE_HOLD_S + PER_CHAR_S * n for n in caption_lengths]
    total = sum(raw)
    if total <= 0:
        return raw
    target = min(max(total, MIN_TOTAL_S), MAX_TOTAL_S)
    return [h * target / total for h in raw]


def _ffmpeg() -> str:
    import imageio_ffmpeg

    return imageio_ffmpeg.get_ffmpeg_exe()


def probe(path: Path) -> tuple[float, str]:
    """(duration in seconds, ffmpeg's stderr) for a media file, read from `ffmpeg -i`."""
    proc = subprocess.run([_ffmpeg(), "-hide_banner", "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)", proc.stderr)
    if m is None:
        raise VideoError(f"cannot read the duration of {path.name}")
    h, mi, s = m.groups()
    return int(h) * 3600 + int(mi) * 60 + float(s), proc.stderr


def _to_mp4(webm: Path, out: Path) -> None:
    cmd = [
        _ffmpeg(), "-y", "-loglevel", "error", "-i", str(webm), "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-movflags", "+faststart", "-an", str(out),
    ]  # fmt: skip
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0 or not out.is_file():
        raise VideoError("ffmpeg could not convert the recording: " + proc.stderr[-300:])


def _finish(out_mp4: Path, chapters: list[Chapter]) -> VideoResult:
    duration, _ = probe(out_mp4)
    (out_mp4.parent / "chapters.json").write_text(
        json.dumps([c.model_dump() for c in chapters], indent=2), encoding="utf-8"
    )
    return VideoResult(path=out_mp4, duration_s=duration, chapters=chapters)


def video_check(result: VideoResult) -> dict[str, Any]:
    """The spec 7a 'MP4 plays (duration > 0)' check, run here because the video is made after QA."""
    ok = result.path.is_file() and result.duration_s > 0
    return {"name": "MP4 plays (duration > 0)", "ok": ok, "detail": f"{result.duration_s:.1f} s"}


def record(
    deck_html_path: Path,
    out_mp4: Path,
    hold_s: float | None = None,
    size: tuple[int, int] = SIZE,
) -> VideoResult:
    """Record the deck at `deck_html_path` to `out_mp4`, plus `chapters.json` beside it."""
    try:
        from playwright.sync_api import Error as PlaywrightError
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover
        raise VideoError("playwright is not installed") from exc
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    width, height = size
    chapters: list[Chapter] = []
    with tempfile.TemporaryDirectory(prefix="poc-video-") as tmp:
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch()
                try:
                    ctx = browser.new_context(
                        viewport={"width": width, "height": height},
                        record_video_dir=tmp,
                        record_video_size={"width": width, "height": height},
                    )
                    page = ctx.new_page()
                    t0 = time.monotonic()
                    page.goto(deck_html_path.resolve().as_uri())
                    page.wait_for_function(
                        "window.__deck && window.__deck.ready === true", timeout=READY_TIMEOUT_MS
                    )
                    slides: list[dict[str, Any]] = page.evaluate(
                        "JSON.parse(document.getElementById('dk-data').textContent).slides"
                    )
                    steps = [(i + 1, s) for i, s in enumerate(slides) if s.get("kind") != "play"]
                    lengths = [
                        len(str(st.get("caption", "")))
                        for _, s in steps
                        for st in (s.get("steps") or [{"caption": s.get("caption", "")}])
                    ]
                    holds = iter(plan_holds(lengths, hold_s))
                    for index, slide in steps:
                        chapters.append(Chapter(t=round(time.monotonic() - t0, 2), title=str(slide["title"])))
                        for n in range(1, max(1, len(slide.get("steps") or [])) + 1):
                            page.evaluate(f"window.__deck.go({index}, {n})")
                            page.wait_for_timeout(next(holds) * 1000)
                    page.close()
                    ctx.close()  # flushes the WebM
                finally:
                    browser.close()
        except PlaywrightError as exc:
            raise VideoError(f"the deck could not be recorded: {str(exc)[:300]}") from exc
        webms = sorted(Path(tmp).glob("*.webm"))
        if not webms:
            raise VideoError("Chromium wrote no recording")
        _to_mp4(webms[0], out_mp4)
    return _finish(out_mp4, chapters)


def _deck_slides(deck_html_path: Path) -> list[dict[str, Any]]:
    html = deck_html_path.read_text(encoding="utf-8")
    m = re.search(r'<script[^>]*id="dk-data"[^>]*>(.*?)</script>', html, re.DOTALL)
    if m is None:
        raise VideoError("the deck has no #dk-data block")
    slides: list[dict[str, Any]] = json.loads(m.group(1)).get("slides", [])
    return slides


def fake_record(deck_html_path: Path, out_mp4: Path, hold_s: float | None = None) -> VideoResult:
    """Dev and E2E only (`VIDEO_FAKE=1`, refused in production): a 2 s black clip with real chapters."""
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        _ffmpeg(), "-y", "-loglevel", "error", "-f", "lavfi", "-i", "color=black:s=320x180:d=2",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", str(out_mp4),
    ]  # fmt: skip
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise VideoError("ffmpeg could not write the fake clip: " + proc.stderr[-300:])
    titles = [str(s["title"]) for s in _deck_slides(deck_html_path) if s.get("kind") != "play"]
    chapters = [Chapter(t=round(i * 2 / max(1, len(titles)), 2), title=t) for i, t in enumerate(titles)]
    return _finish(out_mp4, chapters)
