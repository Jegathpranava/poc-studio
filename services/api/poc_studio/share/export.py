"""The client share zip: `index.html` (summary page), `deck.html`, `walkthrough.mp4` and `summary.pdf`.

Nothing is hosted (amendment 11): the owner sends the zip. Before the zip is written the staging folder goes
through the secret and PII scan. A secret blocks the export (`ShareBlocked`); PII outside the stakeholder
allow-list is only a warning, written to `runs/<id>/share/manifest.json` (which stays out of the zip).
"""

import hashlib
import json
import shutil
import zipfile
from datetime import timedelta
from pathlib import Path

from sqlalchemy import select

from poc_studio.agents.store import next_version, slugify
from poc_studio.config import get_settings
from poc_studio.db.models import Artifact
from poc_studio.db.session import open_session
from poc_studio.qa.secrets import scan_tree
from poc_studio.share import page, tokens
from poc_studio.share.content import latest_path, load_content

PII_KINDS = {"email", "phone"}


class ShareBlocked(RuntimeError):
    """The export holds a secret, or points outside itself. The message carries kinds and files, no values."""


class ShareUnavailable(RuntimeError):
    """The run has nothing to share yet (no deck or no brief)."""


def share_dir(run_id: str) -> Path:
    return get_settings().runs_dir / run_id / "share"


def render_pdf(html: str, out: Path) -> None:
    page.write_pdf(html, out)


def _zip(staging: Path, target: Path) -> None:
    tmp = target.with_name(target.name + ".tmp")
    with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zf:
        for name in ("index.html", "deck.html", "walkthrough.mp4", "summary.pdf"):
            if (staging / name).is_file():
                zf.write(staging / name, name)
    tmp.replace(target)


def _record(run_id: str, rel: str, path: Path) -> None:
    sha = hashlib.sha256(path.read_bytes()).hexdigest()
    full = f"{run_id}/{rel}"
    with open_session() as session:
        row = session.scalar(select(Artifact).where(Artifact.run_id == run_id, Artifact.path == full))
        if row is None:
            session.add(
                Artifact(
                    run_id=run_id, type="share_export", version=next_version(run_id, "share_export"),
                    path=full, sha256=sha,
                )
            )  # fmt: skip
        else:
            row.sha256 = sha
        session.commit()


def latest_zip(run_id: str) -> Path | None:
    path = latest_path(run_id, "share_export", ".zip")
    return path


def build_share_zip(run_id: str) -> Path:
    deck = latest_path(run_id, "deck", ".html")
    if deck is None:
        raise ShareUnavailable("the run has no deck yet")
    content = load_content(run_id)
    root = share_dir(run_id)
    staging = root / "staging"
    shutil.rmtree(staging, ignore_errors=True)
    staging.mkdir(parents=True)
    expires = tokens.clock() + timedelta(days=tokens.TTL_DAYS)

    index = page.render_index(content, expires)
    if problems := page.external_refs(index):
        raise ShareBlocked("index.html points outside itself: " + "; ".join(sorted(set(problems))))
    (staging / "index.html").write_text(index, encoding="utf-8")
    shutil.copyfile(deck, staging / "deck.html")
    video = latest_path(run_id, "video", ".mp4")
    if video is not None:
        shutil.copyfile(video, staging / "walkthrough.mp4")

    findings = scan_tree(staging, pii=True, allow_names=content.stakeholders)
    blockers = [f for f in findings if f.kind not in PII_KINDS]
    if blockers:
        shutil.rmtree(staging, ignore_errors=True)
        kinds = ", ".join(sorted({f"{f.kind} in {f.file}" for f in blockers}))
        raise ShareBlocked(f"a secret was found, nothing was exported: {kinds}")
    warnings = [f"{f.kind} in {f.file}:{f.line}" for f in findings if f.kind in PII_KINDS]

    try:
        render_pdf(page.render_index(content, expires, pdf=True), staging / "summary.pdf")
    except Exception as exc:  # no Chromium, say: the zip is still useful without the PDF
        warnings.append(f"summary.pdf was not made: {type(exc).__name__}")
    (root / "manifest.json").write_text(
        json.dumps({"files": sorted(p.name for p in staging.iterdir()), "warnings": warnings}, indent=2),
        encoding="utf-8",
    )
    target = root / f"{slugify(content.title)}-share.zip"
    _zip(staging, target)
    _record(run_id, f"share/{target.name}", target)
    return target
