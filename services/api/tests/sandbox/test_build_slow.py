"""Real npm: install and build the logistics starter with the fixture ScreenPack ported in (network)."""

import json
from pathlib import Path

import pytest

from poc_studio.agents.port import write_app
from poc_studio.llm.provider import FIXTURE_DIR
from poc_studio.sandbox import runner
from poc_studio.sandbox.fix import PortFix, apply_fix
from poc_studio.schemas.screenpack import ScreenPack
from poc_studio.screens.kits import load_kit

pytestmark = pytest.mark.slow


async def test_port_build_break_and_fix(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    pack = ScreenPack.model_validate(
        json.loads((FIXTURE_DIR / "screens.json").read_text(encoding="utf-8"))[-1]
    )
    pack.screens[0].html += '<p class="braces">a {b} c {{x}} }} &#123;</p>'  # JSX must survive braces
    app = await runner.prepare(tmp_path, "logistics")
    assert not (app / "node_modules").exists() and not (app / ".next").exists()
    write_app(app, pack, load_kit("logistics").icons_css, "Acme prototype")

    inst = await runner.install(app)
    assert inst.ok, inst.log_tail
    built = await runner.build(app, 1)
    assert built.ok, built.log_tail
    assert built.error is None

    broken = app / "app" / "broken" / "page.tsx"
    broken.parent.mkdir(parents=True)
    broken.write_text(
        'import Missing from "../../components/missing";\n\n'
        "export default function Page() {\n  return <Missing />;\n}\n",
        encoding="utf-8",
    )
    bad = await runner.build(app, 2)
    assert not bad.ok and bad.error is not None, bad.log_tail
    assert bad.error.file == "app/broken/page.tsx" and bad.error.line == 1
    assert "missing" in bad.error.message.lower()
    assert "import Missing" in bad.error.excerpt

    fix = PortFix.model_validate_json((FIXTURE_DIR / "port.json").read_text(encoding="utf-8"))
    written, rejected = apply_fix(app, fix)
    assert written == ["app/broken/page.tsx"] and not rejected
    fixed = await runner.build(app, 3)
    assert fixed.ok, fixed.log_tail
    with capsys.disabled():
        print(
            f"\nTIMINGS install={inst.duration_s}s build_ok={built.duration_s}s "
            f"build_fail={bad.duration_s}s build_fixed={fixed.duration_s}s"
        )
