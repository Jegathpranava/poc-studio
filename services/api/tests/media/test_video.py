from pathlib import Path

import pytest

from poc_studio.media.video import VideoError, plan_holds, probe, record, video_check
from poc_studio.schemas.deck import DeckPlan
from tests.deck.conftest import deck_html, icons_css, pack, plan  # noqa: F401 - fixtures reused as is


def test_hold_scaling_fits_120_to_180_for_a_typical_plan() -> None:
    # 10 slides: welcome, overview with 4 steps, 6 areas with 4 steps each, close; ~110 character captions
    lengths = [110] + [110] * 4 + [110] * 24 + [110]
    holds = plan_holds(lengths)
    assert 120 <= sum(holds) <= 180
    assert all(h > 0 for h in holds)


def test_hold_scaling_stretches_short_and_shrinks_long_plans() -> None:
    assert sum(plan_holds([20] * 10)) == pytest.approx(120)
    assert sum(plan_holds([300] * 60)) == pytest.approx(180)
    assert plan_holds([10, 200])[1] > plan_holds([10, 200])[0]  # longer caption, longer hold


def test_fixed_hold_wins() -> None:
    assert plan_holds([10, 500], hold_s=0.3) == [0.3, 0.3]


@pytest.mark.browser
def test_record_makes_h264_mp4_with_chapters(deck_html: str, plan: DeckPlan, tmp_path: Path) -> None:  # noqa: F811
    deck = tmp_path / "deck.html"
    deck.write_text(deck_html, encoding="utf-8")
    out = tmp_path / "out" / "walkthrough.mp4"
    try:
        result = record(deck, out, hold_s=0.3)
    except VideoError as exc:
        if "executable" in str(exc).lower() or "browser" in str(exc).lower():
            pytest.skip(f"no Chromium: {exc}")
        raise
    assert out.is_file() and result.path == out
    duration, stderr = probe(out)
    assert "Video: h264" in stderr
    assert duration > 5 and result.duration_s > 5
    expected = [s.title for s in plan.slides if s.kind != "play"]
    assert [c.title for c in result.chapters] == expected
    assert all(s.title not in [c.title for c in result.chapters] for s in plan.slides if s.kind == "play")
    times = [c.t for c in result.chapters]
    assert times == sorted(times) and times[0] >= 0
    assert (out.parent / "chapters.json").is_file()
    assert not list(out.parent.glob("*.webm"))
    assert video_check(result)["ok"] is True
