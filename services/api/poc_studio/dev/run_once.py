"""Dev CLI: run intake and intelligence on one file.

    uv run python -m poc_studio.dev.run_once <file> [--live]

Uses a throwaway DB and runs dir, so nothing in data/ or runs/ is touched.
"""

import argparse
import asyncio
import os
import shutil
import sys
import tempfile
from pathlib import Path


async def _run(path: Path) -> int:
    from sqlalchemy import select

    from poc_studio.agents.intelligence import run_intelligence
    from poc_studio.config import get_settings
    from poc_studio.db import models  # noqa: F401
    from poc_studio.db.base import Base
    from poc_studio.db.models import AgentStep, Project, Run
    from poc_studio.db.session import get_engine, open_session
    from poc_studio.graph.nodes import intake
    from poc_studio.graph.state import RunState

    Base.metadata.create_all(get_engine())
    settings = get_settings()
    with open_session() as session:
        project = Project(client_name="Dev", client_name_key="dev")
        session.add(project)
        session.flush()
        run = Run(project_id=project.id, title="Dev run", budget_usd=settings.run_budget_usd)
        session.add(run)
        session.commit()
        run_id = run.id
    input_dir = settings.runs_dir / run_id / "input"
    input_dir.mkdir(parents=True)
    shutil.copy(path, input_dir / path.name)

    state: RunState = {"run_id": run_id, "budget": {"limit_usd": settings.run_budget_usd, "spent_usd": 0.0}}
    state = {**state, **await intake(state)}  # pyright: ignore[reportAssignmentType]
    update = await run_intelligence(state)
    req = update["requirements"]
    with open_session() as session:
        step = session.scalars(
            select(AgentStep).where(AgentStep.run_id == run_id, AgentStep.agent == "intelligence")
        ).one()
        print(f"provider : {settings.llm_provider}")
        print(f"title    : {req['title']}  (sector: {req['sector']})")
        print(f"summary  : {req['summary']}")
        print(f"features : {len(req['features'])}")
        tokens = f"{step.tokens_in}+{step.tokens_out}"
        print(f"step     : model={step.model} tokens={tokens} cost=${step.cost_usd:.6f}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="run_once", description=__doc__)
    parser.add_argument("file", type=Path)
    parser.add_argument("--live", action="store_true", help="call the real gateway instead of the mock")
    args = parser.parse_args(argv)
    if not args.file.is_file():
        print(f"no such file: {args.file}", file=sys.stderr)
        return 2
    tmp = Path(tempfile.mkdtemp(prefix="poc-run-once-"))
    os.environ["POC_DATABASE_URL"] = f"sqlite:///{(tmp / 'app.sqlite').as_posix()}"
    os.environ["RUNS_DIR"] = str(tmp / "runs")
    os.environ["LLM_PROVIDER"] = "gateway" if args.live else "mock"
    try:
        return asyncio.run(_run(args.file.resolve()))
    finally:
        from poc_studio.db.session import get_engine

        get_engine().dispose()
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    raise SystemExit(main())
