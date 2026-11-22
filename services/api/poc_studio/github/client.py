"""GitHub REST client (spec section 4): `MockGitHub` for tests and dev, `LiveGitHub` over httpx.

Live needs `GITHUB_MODE=live` and a non-empty token, nothing else turns it on. No message built here ever
holds the token: errors carry the method, path, status and GitHub's own `message` field, redacted.
"""

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol

import httpx

from poc_studio.config import Settings
from poc_studio.redact import redact

API = "https://api.github.com"
API_VERSION = "2022-11-28"
OWNER = "Jegathpranava"  # spec amendment 6: client repos live on the owner's account
TIMEOUT_S = 30.0


class GitHubError(RuntimeError):
    """A GitHub call failed. The message never carries credentials."""


class GitHubNotConfigured(GitHubError):
    """Live mode was asked for without `GITHUB_MODE=live` and a token."""


class RepoNameTaken(GitHubError):
    """The repository name already exists on the account."""


@dataclass(frozen=True)
class RepoInfo:
    owner: str
    name: str
    private: bool
    html_url: str
    clone_url: str


class GitHubClient(Protocol):
    mode: str

    def get_user(self) -> str: ...
    def repo_exists(self, owner: str, name: str) -> bool: ...
    def create_repo(self, name: str, private: bool, description: str) -> RepoInfo: ...
    def create_issue(self, owner: str, repo: str, title: str, body: str) -> str: ...


@dataclass
class MockGitHub:
    """Records the planned calls and returns well-formed fake URLs. No network, no token."""

    existing: set[str] = field(default_factory=set)  # names that already "exist" (tests seed conflicts)
    owner: str = OWNER
    mode: str = "mock"
    calls: list[dict[str, Any]] = field(default_factory=list)
    _issues: int = 0

    def get_user(self) -> str:
        self.calls.append({"call": "get_user"})
        return self.owner

    def repo_exists(self, owner: str, name: str) -> bool:
        self.calls.append({"call": "repo_exists", "owner": owner, "name": name})
        return name.lower() in {n.lower() for n in self.existing}

    def create_repo(self, name: str, private: bool, description: str) -> RepoInfo:
        self.calls.append(
            {"call": "create_repo", "method": "POST", "path": "/user/repos", "name": name, "private": private}
        )
        self.existing.add(name)
        url = f"https://github.com/{self.owner}/{name}"
        return RepoInfo(self.owner, name, private, url, f"{url}.git")

    def create_issue(self, owner: str, repo: str, title: str, body: str) -> str:
        self._issues += 1
        self.calls.append(
            {
                "call": "create_issue",
                "method": "POST",
                "path": f"/repos/{owner}/{repo}/issues",
                "title": title,
            }
        )
        return f"https://github.com/{owner}/{repo}/issues/{self._issues}"

    def record(self, call: str, **data: Any) -> None:
        self.calls.append({"call": call, **data})

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({"mode": "mock", "calls": self.calls}, indent=2), encoding="utf-8")


class LiveGitHub:
    """httpx against api.github.com with `Authorization: Bearer <token>`."""

    mode = "live"

    def __init__(
        self, token: str, *, base_url: str = API, transport: httpx.BaseTransport | None = None
    ) -> None:
        if not token:
            raise GitHubNotConfigured("GITHUB_TOKEN is empty")
        self._token = token
        self._http = httpx.Client(base_url=base_url, transport=transport, timeout=TIMEOUT_S)

    def _request(self, method: str, path: str, **kwargs: Any) -> httpx.Response:
        headers = {
            "Authorization": f"Bearer {self._token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
        }
        try:
            return self._http.request(method, path, headers=headers, **kwargs)
        except httpx.HTTPError as exc:  # the exception text may echo the request: say only what failed
            raise GitHubError(f"GitHub {method} {path} could not be reached ({type(exc).__name__})") from None

    def _fail(self, res: httpx.Response, method: str, path: str) -> GitHubError:
        try:
            detail = str(res.json().get("message", ""))
        except ValueError:
            detail = ""
        text = redact(detail).replace(self._token, "[REDACTED]")[:200]
        hint = " (the token was rejected)" if res.status_code == 401 else ""
        return GitHubError(
            f"GitHub {method} {path} failed with HTTP {res.status_code}{hint}: {text}".rstrip(": ")
        )

    def get_user(self) -> str:
        res = self._request("GET", "/user")
        if res.status_code != 200:
            raise self._fail(res, "GET", "/user")
        return str(res.json()["login"])

    def repo_exists(self, owner: str, name: str) -> bool:
        path = f"/repos/{owner}/{name}"
        res = self._request("GET", path)
        if res.status_code == 404:
            return False
        if res.status_code != 200:
            raise self._fail(res, "GET", path)
        return True

    def create_repo(self, name: str, private: bool, description: str) -> RepoInfo:
        body = {"name": name, "private": private, "description": description[:350], "auto_init": False}
        res = self._request("POST", "/user/repos", json=body)
        if res.status_code == 422 and "already exists" in res.text.lower():
            raise RepoNameTaken(f"a repository named {name} already exists")
        if res.status_code != 201:
            raise self._fail(res, "POST", "/user/repos")
        data = res.json()
        return RepoInfo(
            owner=str(data["owner"]["login"]), name=str(data["name"]), private=bool(data["private"]),
            html_url=str(data["html_url"]), clone_url=str(data["clone_url"]),
        )  # fmt: skip

    def create_issue(self, owner: str, repo: str, title: str, body: str) -> str:
        path = f"/repos/{owner}/{repo}/issues"
        res = self._request("POST", path, json={"title": title[:250], "body": body})
        if res.status_code != 201:
            raise self._fail(res, "POST", path)
        return str(res.json()["html_url"])


def get_github(settings: Settings, *, transport: httpx.BaseTransport | None = None) -> GitHubClient:
    """Mock by default. Live only with `GITHUB_MODE=live` and a token (production refuses mock in config)."""
    if settings.github_mode != "live":
        return MockGitHub()
    token = settings.github_token.get_secret_value()
    if not token:
        raise GitHubNotConfigured("GITHUB_MODE=live needs GITHUB_TOKEN in .env")
    return LiveGitHub(token, transport=transport)
