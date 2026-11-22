"""Repo and DevOps (agent 4): runs after video, reads the Gate 2 options and publishes (mock or live).

A blocked publish (secret scan, QA `block_publish`) or a GitHub or git error fails the step with an error
event, and the run ends `failed`: there is no `delivered` without a repo URL. Only a stub graph in tests
(`POC_ALLOW_STUB_SKIP=1`) may skip when there is nothing to publish.
"""

import asyncio
from typing import Any

from sqlalchemy import select

from poc_studio.agents.store import stub_skip_allowed
from poc_studio.db.models import Project, Run
from poc_studio.db.session import open_session
from poc_studio.events import emit
from poc_studio.github.publish import NothingToPublish, PublishOptions, default_repo_name, publish
from poc_studio.graph.registry import NodeSpec
from poc_studio.graph.state import RunState
from poc_studio.graph.steps import step_scope

AGENT = "repo"


def options_from_state(state: RunState) -> PublishOptions:
    """The approved Gate 2 options; defaults when the approval carried none."""
    saved = (state.get("gate2") or {}).get("edits")
    if saved:
        return PublishOptions.model_validate(saved)
    with open_session() as session:
        row = session.execute(
            select(Project.client_name, Run.title)
            .join(Run, Run.project_id == Project.id)
            .where(Run.id == state["run_id"])
        ).first()
    client, title = row if row else ("client", "poc")
    return PublishOptions(repo_name=default_repo_name(client, title))


async def run_repo(state: RunState) -> dict[str, Any]:
    run_id = state["run_id"]
    async with step_scope(run_id, AGENT):
        try:
            result = await asyncio.to_thread(publish, run_id, options_from_state(state))
        except NothingToPublish as exc:
            if not stub_skip_allowed():
                raise
            emit(run_id, AGENT, "log", message=f"repo skipped: {exc}")
            return {}
        mode = "pushed" if result.pushed else "would push (mock mode)"
        emit(run_id, AGENT, "log", message=f"{mode} to {result.repo_url}, {len(result.issues)} issue(s)")
        return {"repo_url": result.repo_url}


NODE = NodeSpec("repo", run_repo, "repo")
