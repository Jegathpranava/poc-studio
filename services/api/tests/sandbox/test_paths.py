from pathlib import Path

import pytest

from poc_studio.sandbox.fix import FixFile, PortFix, UnsafePath, apply_fix, safe_path

BS = chr(92)  # a backslash
UNSAFE = [
    "../evil.ts",
    "app/../../evil.ts",
    "app/../package.json",
    "/etc/passwd",
    "C:/Windows/x.ts",
    "C:" + BS + "Windows" + BS + "x.ts",
    BS * 2 + "server" + BS + "share" + BS + "x.ts",
    "app" + BS + ".." + BS + "x.ts",
    "package.json",
    "next.config.ts",
    ".env",
    "node_modules/x/index.js",
    "app",
    "components",
    "",
    "~/x.ts",
]


@pytest.mark.parametrize("rel", UNSAFE)
def test_unsafe_paths_are_rejected(tmp_path: Path, rel: str) -> None:
    with pytest.raises(UnsafePath):
        safe_path(tmp_path, rel)


@pytest.mark.parametrize("rel", ["app/page.tsx", "app/fleet/page.tsx", "components/ScreenNav.tsx"])
def test_safe_paths_resolve_inside_the_app(tmp_path: Path, rel: str) -> None:
    assert safe_path(tmp_path, rel).is_relative_to(tmp_path.resolve())


def test_apply_fix_writes_safe_files_and_skips_the_rest(tmp_path: Path) -> None:
    fix = PortFix(
        files=[
            FixFile(path="app/ok/page.tsx", content="export default function P() { return null; }"),
            FixFile(path="../escape.ts", content="x"),
            FixFile(path="package.json", content="{}"),
        ]
    )
    written, rejected = apply_fix(tmp_path, fix)
    assert written == ["app/ok/page.tsx"]
    assert rejected == ["../escape.ts", "package.json"]
    assert (tmp_path / "app/ok/page.tsx").is_file()
    assert not (tmp_path.parent / "escape.ts").exists() and not (tmp_path / "package.json").exists()
