"""Sector kit checks (Task 10): screens only use kit classes, anchors resolve, CSS is scoped."""

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from lxml import html
from lxml.cssselect import CSSSelector

TEMPLATES = Path(__file__).resolve().parents[4] / "templates"
SECTORS = ["logistics", "healthcare", "ecommerce", "fintech"]


def _strip_urls(css: str) -> str:
    return re.sub(r"url\([^)]*\)", "url()", css)


def _strip_comments(css: str) -> str:
    return re.sub(r"/\*.*?\*/", "", css, flags=re.S)


def _kit(sector: str) -> tuple[Path, dict]:
    kit = TEMPLATES / sector / "kit"
    return kit, json.loads((kit / "kit.json").read_text(encoding="utf-8"))


def _defined_classes(kit: Path) -> set[str]:
    out: set[str] = set()
    for name in ("product.css", "icons.css"):
        css = _strip_comments(_strip_urls((kit / name).read_text(encoding="utf-8")))
        out |= set(re.findall(r"\.([A-Za-z_][\w-]*)", css))
    return out


def _fragment(kit: Path, rel: str):
    return html.fromstring(f"<div>{(kit / rel).read_text(encoding='utf-8')}</div>")


def test_sectors_index() -> None:
    idx = json.loads((TEMPLATES / "sectors.json").read_text(encoding="utf-8"))
    assert idx["e-commerce"] == "ecommerce"
    assert sorted(idx.values()) == sorted(SECTORS)


@pytest.mark.parametrize("sector", SECTORS)
def test_kit_json_valid(sector: str) -> None:
    kit, meta = _kit(sector)
    assert meta["sector"] == sector
    assert re.fullmatch(r"[a-z]+", meta["app_class"])
    assert re.fullmatch(r"#[0-9a-fA-F]{6}", meta["accent"])
    assert len(meta["screens"]) == 3
    for scr in meta["screens"]:
        assert set(scr) == {"id", "file", "label", "anchors"}
        assert (kit / scr["file"]).is_file()
    for f in ("product.css", "icons.css", "selectors.md"):
        assert (kit / f).is_file()


@pytest.mark.parametrize("sector", SECTORS)
def test_screen_classes_defined(sector: str) -> None:
    kit, meta = _kit(sector)
    defined = _defined_classes(kit)
    for scr in meta["screens"]:
        root = _fragment(kit, scr["file"])
        used = {c for el in root.iter() for c in (el.get("class") or "").split()}
        assert meta["app_class"] in used
        assert used - defined == set(), f"{scr['id']}: undefined classes {sorted(used - defined)}"
        assert not root.xpath("//*[@style]"), f"{scr['id']}: inline style"


@pytest.mark.parametrize("sector", SECTORS)
def test_anchors(sector: str) -> None:
    kit, meta = _kit(sector)
    for scr in meta["screens"]:
        root = _fragment(kit, scr["file"])
        found = root.xpath("//*[@data-anchor]")
        assert len(found) >= 3, scr["id"]
        assert len(scr["anchors"]) >= 3
        for name in scr["anchors"]:
            assert CSSSelector(f'[data-anchor="{name}"]')(root), f"{scr['id']}: anchor {name} matches nothing"
        assert {e.get("data-anchor") for e in found} == set(scr["anchors"])


@pytest.mark.parametrize("sector", SECTORS)
def test_no_external_urls(sector: str) -> None:
    for path in (TEMPLATES / sector / "kit").rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            assert not re.search(r"https?://", text), f"external URL in {path}"


@pytest.mark.parametrize("sector", SECTORS)
def test_css_scoped(sector: str) -> None:
    kit, meta = _kit(sector)
    prefix = f".pf .{meta['app_class']}"
    css = _strip_comments(_strip_urls((kit / "product.css").read_text(encoding="utf-8")))
    preludes = [p.strip() for p in re.findall(r"([^{}]+)\{", css)]
    assert len(preludes) > 50
    for prelude in preludes:
        if prelude.startswith("@"):
            continue
        for sel in prelude.split(","):
            sel = sel.strip()
            assert sel == prefix or sel.startswith(prefix + " ") or sel.startswith(prefix + "."), sel
    icons = _strip_comments(_strip_urls((kit / "icons.css").read_text(encoding="utf-8")))
    for prelude in re.findall(r"([^{}]+)\{", icons):
        assert prelude.strip().startswith(".pf .ic")
    assert len(re.findall(r"\.pf \.ic-[a-z-]+", icons)) >= 15


@pytest.mark.parametrize("sector", SECTORS)
def test_css_has_no_global_at_rules(sector: str) -> None:
    """@font-face and @import load or define things globally; keyframe names are global too."""
    kit, meta = _kit(sector)
    for name in ("product.css", "icons.css"):
        css = _strip_comments((kit / name).read_text(encoding="utf-8"))
        assert not re.search(r"@(font-face|import)", css, re.I), f"{sector}/{name}"
    css = _strip_comments((kit / "product.css").read_text(encoding="utf-8"))
    for kf in re.findall(r"@(?:-\w+-)?keyframes\s+([^\s{]+)", css):
        assert kf.startswith(meta["app_class"] + "-"), (
            f"{sector}: keyframes {kf} must start with the app class"
        )


@pytest.mark.parametrize("sector", SECTORS)
def test_app_kit_copies_match(sector: str) -> None:
    for f in ("product.css", "icons.css"):
        a = (TEMPLATES / sector / "kit" / f).read_bytes()
        b = (TEMPLATES / sector / "app" / "app" / "kit" / f).read_bytes()
        assert a == b, f"{sector}/{f} copy out of date"


@pytest.mark.slow
@pytest.mark.parametrize("sector", SECTORS)
def test_starter_builds(sector: str, tmp_path: Path) -> None:
    app = tmp_path / sector
    shutil.copytree(TEMPLATES / sector / "app", app, ignore=shutil.ignore_patterns("node_modules", ".next"))
    npm = shutil.which("npm") or "npm"
    for args in (["ci"], ["run", "build"]):
        res = subprocess.run([npm, *args], cwd=app, capture_output=True, text=True, timeout=600)
        assert res.returncode == 0, res.stdout[-2000:] + res.stderr[-2000:]
