import json
import logging

import httpx
import pytest

from poc_studio.config import Settings
from poc_studio.github.client import (
    GitHubError,
    GitHubNotConfigured,
    LiveGitHub,
    MockGitHub,
    RepoNameTaken,
    get_github,
)

TOKEN = "ghp_" + "Zx9Yw8Vv7Uu6Tt5Ss4Rr3Qq2Pp1Oo0"  # fake, split so the source holds no secret


def _client(handler) -> tuple[LiveGitHub, list[httpx.Request]]:  # noqa: ANN001
    seen: list[httpx.Request] = []

    def wrapped(request: httpx.Request) -> httpx.Response:
        seen.append(request)
        return handler(request)

    return LiveGitHub(TOKEN, transport=httpx.MockTransport(wrapped)), seen


def test_get_user_sends_bearer_and_version_headers() -> None:
    gh, seen = _client(lambda r: httpx.Response(200, json={"login": "Jegathpranava"}))
    assert gh.get_user() == "Jegathpranava"
    (req,) = seen
    assert (req.method, req.url.path) == ("GET", "/user")
    assert req.headers["Authorization"] == f"Bearer {TOKEN}"
    assert req.headers["X-GitHub-Api-Version"] == "2022-11-28"
    assert req.headers["Accept"] == "application/vnd.github+json"


def test_create_repo_posts_to_user_repos_private() -> None:
    body = {"name": "acme-poc", "private": True, "owner": {"login": "Jegathpranava"},
            "html_url": "https://github.com/Jegathpranava/acme-poc",
            "clone_url": "https://github.com/Jegathpranava/acme-poc.git"}  # fmt: skip
    gh, seen = _client(lambda r: httpx.Response(201, json=body))
    repo = gh.create_repo("acme-poc", True, "A proof of concept")
    (req,) = seen
    assert (req.method, req.url.path) == ("POST", "/user/repos")
    sent = json.loads(req.content)
    assert sent["name"] == "acme-poc" and sent["private"] is True
    assert repo.html_url.endswith("/Jegathpranava/acme-poc") and repo.private


def test_create_repo_name_clash_is_its_own_error() -> None:
    errors = [{"message": "name already exists on this account"}]
    res = httpx.Response(422, json={"message": "Repository creation failed.", "errors": errors})
    gh, _ = _client(lambda r: res)
    with pytest.raises(RepoNameTaken):
        gh.create_repo("acme-poc", True, "")


def test_create_issue_and_repo_exists() -> None:
    def handler(r: httpx.Request) -> httpx.Response:
        if r.method == "GET":
            return httpx.Response(404 if r.url.path.endswith("missing") else 200, json={})
        return httpx.Response(201, json={"html_url": "https://github.com/o/r/issues/7"})

    gh, seen = _client(handler)
    assert gh.create_issue("o", "r", "Book the kickoff", "Owner: Sam") == "https://github.com/o/r/issues/7"
    assert (seen[0].method, seen[0].url.path) == ("POST", "/repos/o/r/issues")
    assert json.loads(seen[0].content)["title"] == "Book the kickoff"
    assert gh.repo_exists("o", "present") is True
    assert gh.repo_exists("o", "missing") is False
    assert seen[2].url.path == "/repos/o/missing"


def test_errors_never_carry_the_token(caplog: pytest.LogCaptureFixture) -> None:
    echo = {"message": f"Bad credentials for {TOKEN}"}
    gh, _ = _client(lambda r: httpx.Response(401, json=echo))
    with caplog.at_level(logging.DEBUG), pytest.raises(GitHubError) as info:
        gh.get_user()
    assert "401" in str(info.value) and "token was rejected" in str(info.value)
    assert TOKEN not in str(info.value) and TOKEN not in repr(info.value)
    assert TOKEN not in caplog.text


def test_network_errors_do_not_echo_the_request() -> None:
    def boom(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError(f"cannot reach host with {TOKEN}")

    gh, _ = _client(boom)
    with pytest.raises(GitHubError) as info:
        gh.get_user()
    assert TOKEN not in str(info.value) and info.value.__cause__ is None


def test_get_github_refuses_live_without_a_token() -> None:
    with pytest.raises(GitHubNotConfigured):
        get_github(Settings(GITHUB_MODE="live", GITHUB_TOKEN="", _env_file=None))  # type: ignore[call-arg]


def test_get_github_selects_by_mode() -> None:
    assert isinstance(get_github(Settings(GITHUB_MODE="mock", _env_file=None)), MockGitHub)  # type: ignore[call-arg]
    live = get_github(Settings(GITHUB_MODE="live", GITHUB_TOKEN=TOKEN, _env_file=None))  # type: ignore[call-arg]
    assert isinstance(live, LiveGitHub) and TOKEN not in repr(live)


def test_mock_returns_well_formed_urls_and_records_calls() -> None:
    gh = MockGitHub(existing={"taken"})
    assert gh.repo_exists("Jegathpranava", "taken") and not gh.repo_exists("Jegathpranava", "free")
    repo = gh.create_repo("free", True, "d")
    assert repo.html_url == "https://github.com/Jegathpranava/free" and repo.private
    assert (
        gh.create_issue(repo.owner, repo.name, "t", "b") == "https://github.com/Jegathpranava/free/issues/1"
    )
    assert [c["call"] for c in gh.calls] == ["repo_exists", "repo_exists", "create_repo", "create_issue"]
