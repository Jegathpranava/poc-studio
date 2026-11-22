"""Prototype Builder, part 2 (agent 3b): ScreenPack in, a Next.js app that builds out.

Flow: copy the sector starter, write the kit CSS and one page per screen (deterministic HTML to JSX), run
`npm ci` once, then `npm run build` up to 3 times. After a failed build the `smart` model gets the error, the
excerpt and the failing file, and returns replacement files (confined to `app/` and `components/`).

A failed port must not block Gate 2 (spec 7b), but `step_scope` re-raises and the graph would abort the run.
So `run_port` raises `PortFailed` inside `step_scope` (the step ends `failed` with an error event), catches
it outside, and returns `{"port_result": {"ok": False, "error": ...}}` so the graph goes on to assemble, QA
and Gate 2. Other exceptions (budget pause, bugs) still propagate.
"""

import asyncio
import hashlib
import json
from pathlib import Path
from typing import Any

from sqlalchemy import select

from poc_studio.agents.screens import _latest  # pyright: ignore[reportPrivateUsage]
from poc_studio.config import get_settings
from poc_studio.db.models import AgentStep, Artifact, Run
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.spend import node_budget
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope
from poc_studio.llm import RunBudget, SchemaError, complete_json, wrap_untrusted
from poc_studio.preview import get_preview_manager
from poc_studio.sandbox import runner
from poc_studio.sandbox.errors import BuildError
from poc_studio.sandbox.fix import PortFix, UnsafePath, apply_fix, safe_path
from poc_studio.sandbox.jsx import page_source
from poc_studio.schemas.requirements import Requirements
from poc_studio.schemas.screenpack import ScreenPack
from poc_studio.screens.kits import load_kit, sector_dir

AGENT = "port"
RESULT_KEY = "port_result"
MAX_ATTEMPTS = 3
MAX_TOKENS = 8000
SYSTEM = (
    "You fix a Next.js 16 (App Router, React 19, TypeScript strict) build error in a generated prototype. "
    "Change as little as possible. Keep every class name and all CSS verbatim; do not restyle anything. "
    "Do not add dependencies. Return only the files that must change, each with its full new content. "
    "Paths are relative to the app root and must start with `app/` or `components/`."
)

NAV_CSS = """
.screen-nav { position: fixed; left: 50%; bottom: 12px; transform: translateX(-50%); z-index: 50;
  display: flex; gap: 4px; max-width: calc(100vw - 24px); overflow-x: auto; padding: 4px;
  border-radius: 999px; background: rgba(20, 24, 31, 0.92); font: 500 12px/1 system-ui, sans-serif; }
.screen-nav-link { padding: 7px 12px; border-radius: 999px; color: #d6dbe4; text-decoration: none;
  white-space: nowrap; }
.screen-nav-link.is-active { background: #ffffff; color: #14181f; }
"""


class PortFailed(RuntimeError):
    def __init__(self, message: str, error: BuildError | None = None) -> None:
        super().__init__(message)
        self.error = error


def route_file(route: str) -> str:
    slug = route.strip("/")
    if slug and not all(c.isalnum() or c == "-" for c in slug):
        raise ValueError(f"bad route {route!r}")
    return f"app/{slug}/page.tsx" if slug else "app/page.tsx"


def _write(app_dir: Path, rel: str, content: str) -> None:
    target = app_dir / rel
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")


def layout_source(title: str) -> str:
    return (
        'import type { ReactNode } from "react";\n'
        'import "./kit/product.css";\nimport "./kit/icons.css";\nimport "./globals.css";\n'
        'import ScreenNav from "../components/ScreenNav";\n\n'
        f"export const metadata = {{ title: {json.dumps(title)} }};\n\n"
        "export default function RootLayout({ children }: { children: ReactNode }) {\n"
        '  return (\n    <html lang="en">\n      <body>\n        {children}\n        <ScreenNav />\n'
        "      </body>\n    </html>\n  );\n}\n"
    )


def nav_source(pack: ScreenPack) -> str:
    items = [{"href": s.route, "label": s.label} for s in pack.screens]
    return (
        '"use client";\n\nimport Link from "next/link";\nimport { usePathname } from "next/navigation";\n\n'
        f"const SCREENS = {json.dumps(items, indent=2)};\n\n"
        "export default function ScreenNav() {\n  const path = usePathname();\n  return (\n"
        '    <nav className="screen-nav" aria-label="Prototype screens">\n'
        "      {SCREENS.map((s) => (\n"
        "        <Link\n          key={s.href}\n          href={s.href}\n"
        '          className={"screen-nav-link" + (path === s.href ? " is-active" : "")}\n'
        "        >\n          {s.label}\n        </Link>\n      ))}\n    </nav>\n  );\n}\n"
    )


def write_app(app_dir: Path, pack: ScreenPack, icons_css: str, title: str) -> list[str]:
    """Kit CSS, layout, nav and one page per screen. Returns the relative paths written."""
    _write(app_dir, "app/kit/product.css", pack.product_css)
    _write(app_dir, "app/kit/icons.css", icons_css)
    globals_css = app_dir / "app" / "globals.css"
    existing = globals_css.read_text(encoding="utf-8") if globals_css.is_file() else ""
    _write(app_dir, "app/globals.css", existing.rstrip() + "\n" + NAV_CSS)
    _write(app_dir, "app/layout.tsx", layout_source(title))
    _write(app_dir, "components/ScreenNav.tsx", nav_source(pack))
    hrefs = {s.label.strip().lower(): s.route for s in pack.screens}
    written = ["app/kit/product.css", "app/kit/icons.css", "app/layout.tsx", "components/ScreenNav.tsx"]
    for s in pack.screens:
        rel = route_file(s.route)
        _write(app_dir, rel, page_source(s.id, s.html, hrefs))
        written.append(rel)
    return written


def fix_prompt(error: BuildError, failing: str) -> str:
    return (
        "The production build failed.\n\n"
        f"File: {error.file or '(unknown)'}  line {error.line}, column {error.col}\n"
        f"Error: {error.message}\n\n"
        "Excerpt around the error (`>` marks the line):\n"
        + wrap_untrusted(error.excerpt or "(none)")
        + "\n\nFull content of the failing file:\n"
        + wrap_untrusted(failing or "(file not found)")
        + "\n\nReturn the corrected files as JSON."
    )


def _read_failing(app_dir: Path, error: BuildError) -> str:
    if not error.file:
        return ""
    try:
        return safe_path(app_dir, error.file).read_text(encoding="utf-8")[:20_000]
    except (UnsafePath, OSError, UnicodeDecodeError):
        return ""


def _tree_hash(app_dir: Path) -> str:
    h = hashlib.sha256()
    for root in ("app", "components"):
        for path in sorted((app_dir / root).rglob("*")):
            if path.is_file():
                h.update(path.relative_to(app_dir).as_posix().encode())
                h.update(path.read_bytes())
    return h.hexdigest()


def persist_prototype(run_id: str, app_dir: Path, build_info: dict[str, Any]) -> int:
    """One `prototype` row (path = the app dir; the code lives on disk) and `build.json` next to it."""
    (app_dir.parent / "build.json").write_text(json.dumps(build_info, indent=2), encoding="utf-8")
    path = f"{run_id}/app"
    sha = _tree_hash(app_dir)
    with open_session() as session:
        row = session.scalars(
            select(Artifact).where(
                Artifact.run_id == run_id, Artifact.type == "prototype", Artifact.path == path
            )
        ).first()
        if row is None:
            row = Artifact(run_id=run_id, type="prototype", version=1, path=path, sha256=sha)
            session.add(row)
        else:  # a send-back reruns the port: same path, next version
            row.version, row.sha256 = row.version + 1, sha
        session.commit()
        return row.version


def _set_step(step_id: int, **fields: Any) -> None:
    with open_session() as session:
        row = session.get(AgentStep, step_id)
        if row is not None:
            for k, v in fields.items():
                setattr(row, k, v)
            session.commit()


async def _fix(
    run_id: str, app_dir: Path, error: BuildError, model: str, run: RunBudget, totals: dict[str, Any]
) -> None:
    try:
        result = await complete_json(
            agent=AGENT, model=model, system=SYSTEM, user=fix_prompt(error, _read_failing(app_dir, error)),
            schema=PortFix, max_tokens=MAX_TOKENS, run=run,
        )  # fmt: skip
    except SchemaError as exc:
        emit(run_id, AGENT, "log", message=f"fix reply invalid: {str(exc)[:200]}")
        return
    totals["in"] += result.tokens_in
    totals["out"] += result.tokens_out
    totals["cost"] += result.cost_usd
    written, rejected = apply_fix(app_dir, result.value)
    emit(run_id, AGENT, "log", message=f"fix wrote {len(written)} file(s), rejected {len(rejected)}")


async def reset_previous_build(run_id: str) -> None:
    """A rebuild must not run under a live preview server, nor keep the last attempt's `build.json`."""
    manager = get_preview_manager()
    if manager is not None:
        await manager.stop(run_id)
    (get_settings().runs_dir / run_id / "build.json").unlink(missing_ok=True)


async def _port(state: RunState, step_id: int, model: str, budget: RunBudget) -> dict[str, Any]:
    run_id = state["run_id"]
    pack = _latest(state, "screenpack", ScreenPack)
    if pack is None:
        raise ValueError("no screenpack artifact to port")
    req = _latest(state, "requirements", Requirements)
    sector = sector_dir(req.sector if req else "other", " ".join(s.label for s in pack.screens))
    kit = load_kit(sector)
    await reset_previous_build(run_id)
    app_dir = await runner.prepare(get_settings().runs_dir / run_id, sector)
    title = f"{req.client} prototype" if req else "Prototype"
    written = await asyncio.to_thread(write_app, app_dir, pack, kit.icons_css, title)
    emit(run_id, AGENT, "log", message=f"wrote {len(written)} files from {len(pack.screens)} screens")

    inst = await runner.install(app_dir)
    state_word = "ok" if inst.ok else "failed"
    emit(run_id, AGENT, "log", message=f"npm ci {state_word} in {inst.duration_s:.0f} s")
    if not inst.ok:
        detail = "npm ci failed: " + inst.log_tail[-300:]
        raise PortFailed("Install failed", BuildError(file="", line=0, col=0, message=detail))

    totals: dict[str, Any] = {"in": 0, "out": 0, "cost": 0.0}
    result = None
    for attempt in range(1, MAX_ATTEMPTS + 1):
        _set_step(step_id, attempt=attempt)
        result = await runner.build(app_dir, attempt)
        outcome = "ok" if result.ok else "failed: " + (result.error.message if result.error else "")
        emit(run_id, AGENT, "log", attempt=attempt, message=f"build attempt {attempt} {outcome}")
        if result.ok or attempt == MAX_ATTEMPTS:
            break
        if result.error is not None:
            await _fix(run_id, app_dir, result.error, model, budget, totals)
    assert result is not None
    _set_step(step_id, tokens_in=totals["in"], tokens_out=totals["out"], cost_usd=totals["cost"], model=model)
    with open_session() as session:
        run = session.get(Run, run_id)
        if run is not None:
            run.tokens_total += totals["in"] + totals["out"]
            session.commit()
    if totals["in"] or totals["out"]:
        emit(
            run_id, AGENT, "cost", model=model, tokens_in=totals["in"], tokens_out=totals["out"],
            cost_usd=totals["cost"],
        )  # fmt: skip
    info = {**result.model_dump(mode="json"), "install_s": inst.duration_s, "attempts": result.attempt}
    persist_prototype(run_id, app_dir, info)
    if not result.ok:
        error = result.error or BuildError(file="", line=0, col=0, message="Build failed")
        text = f"Attempt {MAX_ATTEMPTS} of {MAX_ATTEMPTS}"
        emit(
            run_id, AGENT, "error", status="failed", attempt=MAX_ATTEMPTS, message=text,
            error=error.model_dump(),
        )  # fmt: skip
        raise PortFailed(text, error)
    return {"ok": True, **info}


async def run_port(state: RunState) -> dict[str, Any]:
    run_id = state["run_id"]
    model = get_settings().default_smart_model
    budget = node_budget(state)
    try:
        async with step_scope(run_id, AGENT, model=model) as step_id:
            outcome = await _port(state, step_id, model, budget)
    except PortFailed as exc:  # the step is already `failed`; the run goes on to Gate 2
        err = exc.error.model_dump() if exc.error else {"message": str(exc)}
        failed = {"ok": False, "error": err}
        return {RESULT_KEY: failed, "build_result": failed, "spent_delta": budget.charged_usd}
    return {RESULT_KEY: outcome, "build_result": outcome, "spent_delta": budget.charged_usd}


NODE = NodeSpec("port", run_port, "port")
