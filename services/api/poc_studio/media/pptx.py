"""Static 16:9 .pptx of a DeckPlan (python-pptx). Plain neutral styling with the pack's accent colour."""

from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.util import Emu, Inches, Pt

from poc_studio.schemas.deck import DeckPlan, Slide
from poc_studio.schemas.screenpack import ScreenPack

INK = RGBColor(0x1F, 0x23, 0x28)
MUTED = RGBColor(0x5F, 0x66, 0x6D)


def _rgb(hex_color: str) -> RGBColor:
    return RGBColor.from_string(hex_color.lstrip("#").upper())


def _text(slide, left: float, top: float, width: float, height: float, text: str, size: int,  # noqa: ANN001
          color: RGBColor = INK, bold: bool = False) -> None:  # fmt: skip
    box = slide.shapes.add_textbox(Inches(left), Inches(top), Inches(width), Inches(height))
    frame = box.text_frame
    frame.word_wrap = True
    run = frame.paragraphs[0].add_run()
    run.text = text
    run.font.size, run.font.bold, run.font.color.rgb = Pt(size), bold, color


def _figure_value(value: float) -> str:
    return f"{value:,.0f}" if float(value).is_integer() else f"{value:,.2f}"


def _add_slide(prs, plan: DeckPlan, slide: Slide, accent: RGBColor) -> None:  # noqa: ANN001
    s = prs.slides.add_slide(prs.slide_layouts[6])
    bar = s.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, Emu(prs.slide_width), Inches(0.18))
    bar.fill.solid()
    bar.fill.fore_color.rgb = accent
    bar.line.fill.background()
    if slide.eyebrow:
        _text(s, 0.7, 0.45, 11.9, 0.4, slide.eyebrow.upper(), 14, accent, bold=True)
    _text(s, 0.7, 0.9, 11.9, 1.2, slide.title, 36, bold=True)
    _text(s, 0.7, 2.0, 11.9, 1.0, slide.caption, 20, MUTED)
    if slide.steps:
        box = s.shapes.add_textbox(Inches(0.7), Inches(3.1), Inches(11.9), Inches(3.6))
        frame = box.text_frame
        frame.word_wrap = True
        for i, step in enumerate(slide.steps):
            para = frame.paragraphs[0] if i == 0 else frame.add_paragraph()
            para.space_after = Pt(8)
            lead = para.add_run()
            lead.text = f"\u2022 {step.title}: "
            lead.font.size, lead.font.bold, lead.font.color.rgb = Pt(18), True, INK
            body = para.add_run()
            body.text = step.caption
            body.font.size, body.font.color.rgb = Pt(18), MUTED
    if slide.figures:
        width = 11.9 / len(slide.figures)
        for i, fig in enumerate(slide.figures):
            left = 0.7 + i * width
            _text(s, left, 3.3, width - 0.2, 1.3, _figure_value(fig.value), 54, accent, bold=True)
            _text(s, left, 4.7, width - 0.2, 0.6, fig.label, 18, INK, bold=True)
            _text(s, left, 5.3, width - 0.2, 0.6, fig.source, 12, MUTED)
    _text(s, 0.7, 6.95, 11.9, 0.4, plan.data_note, 11, MUTED)


def build_pptx(plan: DeckPlan, pack: ScreenPack, path: Path) -> Path:
    """Write one slide per plan slide to `path`."""
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    accent = _rgb(plan.accent or pack.accent)
    for slide in plan.slides:
        _add_slide(prs, plan, slide, accent)
    path.parent.mkdir(parents=True, exist_ok=True)
    prs.save(str(path))
    return path
