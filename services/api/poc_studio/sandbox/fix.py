"""The model's build fix: a few files to overwrite, confined to `app/` and `components/` of the starter."""

from pathlib import Path, PurePosixPath

from pydantic import BaseModel, Field

ALLOWED_ROOTS = ("app", "components")
MAX_FILE_CHARS = 60_000


class UnsafePath(ValueError):
    pass


class FixFile(BaseModel):
    path: str
    content: str = Field(max_length=MAX_FILE_CHARS)


class PortFix(BaseModel):
    files: list[FixFile] = Field(min_length=1, max_length=8)


def safe_path(app_dir: Path, rel: str) -> Path:
    """Resolve `rel` inside `app_dir`, or raise UnsafePath (`..`, absolute, outside app/ and components/)."""
    if (
        not rel
        or "\x00" in rel
        or "\\" in rel
        or rel.startswith(("/", "~"))
        or PurePosixPath(rel).is_absolute()
    ):
        raise UnsafePath(f"not a relative path: {rel!r}")
    parts = PurePosixPath(rel).parts
    if any(":" in part for part in parts) or ".." in parts or "." in parts:
        raise UnsafePath(f"path escapes the app: {rel!r}")
    if parts[0] not in ALLOWED_ROOTS or len(parts) < 2:
        raise UnsafePath(f"only app/ and components/ may be written: {rel!r}")
    target = (app_dir / rel).resolve()
    if not target.is_relative_to(app_dir.resolve()):
        raise UnsafePath(f"path escapes the app: {rel!r}")
    return target


def apply_fix(app_dir: Path, fix: PortFix) -> tuple[list[str], list[str]]:
    """Write the safe files. Returns (written paths, rejected paths); one bad path never blocks the rest."""
    written: list[str] = []
    rejected: list[str] = []
    for f in fix.files:
        try:
            target = safe_path(app_dir, f.path)
        except UnsafePath:
            rejected.append(f.path)
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(f.content, encoding="utf-8", newline="\n")
        written.append(f.path)
    return written, rejected
