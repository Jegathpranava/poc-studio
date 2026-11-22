"""GET /api/templates: the sector kits with usage and first-time-build stats computed from the runs."""

import json
from pathlib import Path

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.orm import Session

from poc_studio.config import REPO_ROOT, get_settings
from poc_studio.db.models import Project, Run
from poc_studio.db.session import get_session

router = APIRouter()
TEMPLATES_DIR = REPO_ROOT / "templates"


class TemplateStat(BaseModel):
    sector: str
    app_class: str
    accent: str
    screens: int
    runs_used: int
    builds_counted: int  # runs of this sector that have a build.json
    first_time_ok: int  # of those, built on attempt 1
    first_time_build_rate: float | None  # first_time_ok / builds_counted, None until a build exists


def _first_time_ok(runs_dir: Path, run_id: str) -> bool | None:
    """True when the run built on attempt 1, False when it needed more or failed, None without a build."""
    path = runs_dir / run_id / "build.json"
    try:
        info = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return bool(info.get("ok")) and int(info.get("attempts") or 1) == 1


def _kits() -> list[tuple[str, dict[str, object]]]:
    try:
        mapping: dict[str, str] = json.loads((TEMPLATES_DIR / "sectors.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    kits: list[tuple[str, dict[str, object]]] = []
    for sector, folder in mapping.items():
        try:
            kit = json.loads((TEMPLATES_DIR / folder / "kit" / "kit.json").read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        kits.append((sector, kit))
    return kits


@router.get("/templates", response_model=list[TemplateStat])
def list_templates(session: Session = Depends(get_session)) -> list[TemplateStat]:
    rows = session.execute(select(Run.id, Project.sector).join(Project, Project.id == Run.project_id)).all()
    by_sector: dict[str, list[str]] = {}
    for run_id, sector in rows:
        by_sector.setdefault(sector or "", []).append(run_id)
    runs_dir = get_settings().runs_dir
    out: list[TemplateStat] = []
    for sector, kit in _kits():
        ids = by_sector.get(sector, [])
        results = [r for r in (_first_time_ok(runs_dir, i) for i in ids) if r is not None]
        ok = sum(results)
        screens = kit.get("screens")
        out.append(
            TemplateStat(
                sector=sector,
                app_class=str(kit.get("app_class", "")),
                accent=str(kit.get("accent", "")),
                screens=len(screens) if isinstance(screens, list) else 0,
                runs_used=len(ids),
                builds_counted=len(results),
                first_time_ok=ok,
                first_time_build_rate=ok / len(results) if results else None,
            )
        )
    return out
