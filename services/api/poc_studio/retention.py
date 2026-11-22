"""Retention (spec 8): delete the uploaded inputs of old runs, keep every generated artifact."""

import logging
import shutil
from datetime import timedelta

from sqlalchemy import select

from poc_studio.config import Settings
from poc_studio.db.models import Run, now
from poc_studio.db.session import open_session

log = logging.getLogger(__name__)


def apply_retention(settings: Settings) -> int:
    """Delete `runs/<id>/input/` of runs started more than `retention_days` ago. 0 days turns it off.
    Returns the number of folders deleted and logs only that count (never a file name or content)."""
    days = settings.retention_days
    if days <= 0:
        return 0
    cutoff = now() - timedelta(days=days)
    with open_session() as session:
        old = session.scalars(select(Run.id).where(Run.started_at < cutoff, Run.status != "running")).all()
    deleted = 0
    for run_id in old:
        target = settings.runs_dir / run_id / "input"
        if target.is_dir():
            shutil.rmtree(target, ignore_errors=True)
            deleted += 1
    if deleted:
        log.info("retention removed the inputs of %d run(s)", deleted)
    return deleted
