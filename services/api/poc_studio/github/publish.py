"""Publish a run to GitHub: build the repo folder, scan it, create the repo, push, file issues.

Order inside `publish`: secret scan, QA `block_publish`, create repo (private by default, `-2` suffix on a
name clash), push, issues, `repo` artifact. Nothing reaches GitHub before both blocks pass. In mock mode
git still inits and commits locally, but nothing is pushed.

The token goes to git through `GIT_CONFIG_*` environment variables (`http.extraheader`), so it is never in
the remote URL, in `.git/config` or on a command line. Git's output is redacted before it is returned.
"""

import json
import os
import re
import shutil
import stat
import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select

from poc_studio.agents.store import latest_json, next_version, record, slugify
from poc_studio.config import get_settings
from poc_studio.db.models import Artifact
from poc_studio.db.session import open_session
from poc_studio.github.client import (
    GitHubClient,
    GitHubError,
    MockGitHub,
    RepoInfo,
    RepoNameTaken,
    get_github,
)
from poc_studio.github.readme import build_readme, ci_workflow, env_example
from poc_studio.qa.secrets import DEFAULT_EXCLUDE, scan_tree
from poc_studio.redact import redact
from poc_studio.routes.schemas import REPO_NAME_PATTERN
from poc_studio.schemas.architecture import Architecture
from poc_studio.schemas.deck import DeckPlan
from poc_studio.schemas.requirements import Requirements

EXCLUDE_COPY = ("node_modules", ".next", ".home", ".git", ".env", ".env.local")
MAX_VIDEO_BYTES = 50 * 1024 * 1024
AUTHOR = ("PoC Studio", "noreply@example.com")
MAX_NAME_TRIES = 20
GIT_TIMEOUT_S = 120


class PublishBlocked(RuntimeError):
    """The publish must not go ahead. The message names kinds and locations, never secret values."""


class NothingToPublish(PublishBlocked):
    """There is no app, brief, architecture or deck plan to build the repo from."""


class PublishFailed(RuntimeError):
    """A git step failed. The message is redacted."""


class PublishOptions(BaseModel):
    repo_name: str = Field(pattern=REPO_NAME_PATTERN)
    private: bool = True
    open_issues: bool = True
    add_ci: bool = True

    @field_validator("repo_name")
    @classmethod
    def _allowed_by_github(cls, v: str) -> str:
        if v in (".", "..") or v.endswith(".git"):
            raise ValueError("GitHub does not allow this repository name")
        return v


class PublishResult(BaseModel):
    repo_url: str
    name: str
    private: bool
    issues: list[str]
    pushed: bool
    mode: str
    file_count: int
    commit: str | None = None


def default_repo_name(client: str, title: str) -> str:
    """Slug of client and title plus `-poc` (the title often repeats the client and already says PoC)."""
    c, t = slugify(client), slugify(title).removesuffix("-poc")
    base = t if t.startswith(c) else f"{c}-{t}"
    return f"{base[:90].strip('-')}-poc"


# --- the repo folder ------------------------------------------------------------------------------
def _latest_path(run_id: str, kind: str, suffix: str, name: str = "") -> Path | None:
    with open_session() as session:
        row = session.scalars(
            select(Artifact)
            .where(Artifact.run_id == run_id, Artifact.type == kind, Artifact.path.like(f"%{name}%{suffix}"))
            .order_by(Artifact.version.desc())
        ).first()
        rel = row.path if row else None
    file = get_settings().runs_dir / rel if rel else None
    return file if file is not None and file.is_file() else None


def _rmtree(path: Path) -> None:
    def unlock(func: Callable[[str], object], target: str, _exc: BaseException) -> None:
        os.chmod(target, stat.S_IWRITE)  # git marks pack files read-only on Windows
        func(target)

    if path.exists():
        shutil.rmtree(path, onexc=unlock)


def publish_dir(run_id: str) -> Path:
    return get_settings().runs_dir / run_id / "publish"


def _copy(src: Path | None, dest: Path) -> bool:
    if src is None:
        return False
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, dest)
    return True


def prepare_repo_dir(run_id: str, *, add_ci: bool = True) -> Path:
    """Fresh `runs/<id>/publish/`: the app plus README, .env.example, CI, docs/ and deck/."""
    app = get_settings().runs_dir / run_id / "app"
    if not app.is_dir():
        raise NothingToPublish("There is no prototype code to publish: the port step did not produce an app.")
    state: Any = {"run_id": run_id}
    req = latest_json(state, "requirements", Requirements)
    arch = latest_json(state, "architecture", Architecture)
    plan = latest_json(state, "deck", DeckPlan)
    if req is None or arch is None or plan is None:
        raise NothingToPublish(
            "The brief, architecture or deck plan is missing, so the README cannot be built."
        )
    dest = publish_dir(run_id)
    _rmtree(dest)
    shutil.copytree(app, dest, ignore=shutil.ignore_patterns(*EXCLUDE_COPY))
    docs = [
        f"docs/{n}.md"
        for n in ("exec-summary", "user-flows")
        if _copy(_latest_path(run_id, "docs", ".md", n), dest / "docs" / f"{n}.md")
    ]
    deck: list[str] = []
    if _copy(_latest_path(run_id, "deck", ".html"), dest / "deck" / "deck.html"):
        deck.append("deck/deck.html")
    video = _latest_path(run_id, "video", ".mp4")
    if video is not None and video.stat().st_size <= MAX_VIDEO_BYTES:
        _copy(video, dest / "deck" / "walkthrough.mp4")
        deck.append("deck/walkthrough.mp4")
    (dest / "README.md").write_text(build_readme(req, arch, plan, docs=docs, deck=deck), encoding="utf-8")
    (dest / ".env.example").write_text(env_example(req.title), encoding="utf-8")
    if not (dest / ".gitignore").is_file():
        ignore = "node_modules/\n.next/\n.env\n.env.*\n!.env.example\n"
        (dest / ".gitignore").write_text(ignore, encoding="utf-8")
    if add_ci:
        ci = dest / ".github" / "workflows" / "ci.yml"
        ci.parent.mkdir(parents=True, exist_ok=True)
        ci.write_text(ci_workflow((dest / "package-lock.json").is_file()), encoding="utf-8")
    return dest


# --- git ------------------------------------------------------------------------------------------
def _git_env(token: str | None) -> dict[str, str]:
    env = {k: v for k, v in os.environ.items() if not re.search(r"TOKEN|SECRET|KEY|PASSWORD", k, re.I)}
    env |= {
        "GIT_TERMINAL_PROMPT": "0", "GIT_AUTHOR_NAME": AUTHOR[0], "GIT_AUTHOR_EMAIL": AUTHOR[1],
        "GIT_COMMITTER_NAME": AUTHOR[0], "GIT_COMMITTER_EMAIL": AUTHOR[1],
    }  # fmt: skip
    if token:  # per-process config: never written to .git/config, never on a command line
        env |= {
            "GIT_CONFIG_COUNT": "1",
            "GIT_CONFIG_KEY_0": "http.extraheader",
            "GIT_CONFIG_VALUE_0": f"AUTHORIZATION: bearer {token}",
        }
    return env


def _git(cwd: Path, args: list[str], token: str | None = None) -> str:
    try:
        res = subprocess.run(
            ["git", "-c", "credential.helper=", *args], cwd=cwd, env=_git_env(token),
            capture_output=True, text=True, timeout=GIT_TIMEOUT_S, check=False,
        )  # fmt: skip
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise PublishFailed(f"git {args[0]} did not run ({type(exc).__name__})") from None
    out = f"{res.stdout}\n{res.stderr}"
    if token:
        out = out.replace(token, "[REDACTED]")
    if res.returncode != 0:
        raise PublishFailed(f"git {args[0]} failed: {redact(out).strip()[:300]}")
    return redact(out)


def push(directory: Path, remote_url: str, token: str | None, *, mock: bool = False) -> tuple[bool, str]:
    """Init, commit and (live only) push `main`. Returns (pushed, commit sha). Mock stays offline."""
    _git(directory, ["init", "-b", "main"])
    _git(directory, ["add", "-A"])
    _git(directory, ["commit", "--no-verify", "-m", "Initial commit from PoC Studio"])
    sha = _git(directory, ["rev-parse", "HEAD"]).strip().splitlines()[0]
    if mock:
        return False, sha
    if not token:
        raise PublishFailed("no GitHub token to push with")
    _git(directory, ["remote", "add", "origin", remote_url])
    _git(directory, ["push", "-u", "origin", "main"], token)
    return True, sha


# --- publish --------------------------------------------------------------------------------------
def _file_count(directory: Path) -> int:
    return sum(
        1 for p in directory.rglob("*") if p.is_file() and ".git" not in p.relative_to(directory).parts
    )


def latest_qa_report(run_id: str) -> dict[str, Any] | None:
    path = _latest_path(run_id, "qa_report", ".json")
    return json.loads(path.read_text(encoding="utf-8")) if path else None


def _check_clean(directory: Path) -> None:
    findings = scan_tree(directory, DEFAULT_EXCLUDE + (".git",))
    if findings:
        where = ", ".join(f"{f.file}:{f.line} {f.kind}" for f in findings[:10])
        raise PublishBlocked(f"Secret scan blocked the push: {len(findings)} finding(s) at {where}.")


def _create_repo(gh: GitHubClient, owner: str, options: PublishOptions, description: str) -> RepoInfo:
    for n in range(1, MAX_NAME_TRIES + 1):
        name = options.repo_name if n == 1 else f"{options.repo_name}-{n}"
        if gh.repo_exists(owner, name):
            continue
        try:
            return gh.create_repo(name, options.private, description)
        except RepoNameTaken:
            continue  # another repo took the name between the check and the create
    raise GitHubError(f"No free repository name found after {MAX_NAME_TRIES} tries for {options.repo_name}")


def _open_issues(gh: GitHubClient, repo: RepoInfo, req: Requirements) -> list[str]:
    urls: list[str] = []
    for item in req.action_items:
        lines = [f"Owner: {item.owner}" if item.owner else "", f"Due: {item.due}" if item.due else ""]
        body = "\n".join(x for x in lines if x) or "From the kickoff meeting."
        urls.append(gh.create_issue(repo.owner, repo.name, item.text[:120], body))
    return urls


def publish(run_id: str, options: PublishOptions, *, github: GitHubClient | None = None) -> PublishResult:
    settings = get_settings()
    directory = prepare_repo_dir(run_id, add_ci=options.add_ci)
    _check_clean(directory)
    report = latest_qa_report(run_id)
    if report and report.get("block_publish"):
        raise PublishBlocked("QA blocked the publish: a secret was found in the generated files.")
    gh = github or get_github(settings)
    req = latest_json({"run_id": run_id}, "requirements", Requirements)
    repo = _create_repo(gh, gh.get_user(), options, (req.summary if req else "")[:300])
    mock = gh.mode == "mock"
    token = None if mock else settings.github_token.get_secret_value()
    pushed, sha = push(directory, repo.clone_url, token, mock=mock)
    issues = _open_issues(gh, repo, req) if options.open_issues and req is not None else []
    result = PublishResult(
        repo_url=repo.html_url, name=repo.name, private=repo.private, issues=issues, pushed=pushed,
        mode=gh.mode, file_count=_file_count(directory), commit=sha,
    )  # fmt: skip
    if isinstance(gh, MockGitHub):
        gh.record("push", would_push=True, remote=repo.clone_url, branch="main")
        gh.write(settings.runs_dir / run_id / "publish.mock.json")
    version = next_version(run_id, "repo")
    record(run_id, "repo", version, f"publish.v{version}.json", result.model_dump_json(indent=2).encode())
    return result
