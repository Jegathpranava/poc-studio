import json
from pathlib import Path
from typing import Any

from poc_studio.config import get_settings
from tests.graph.conftest import create_run, wait_status

FILES = "/api/runs/{}/files"
BUILD = "/api/runs/{}/build"
PREVIEW = "/api/runs/{}/preview"


def write(root: Path, rel: str, text: str = "x") -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def names(nodes: list[dict[str, Any]]) -> list[str]:
    return [n["name"] for n in nodes]


def test_file_tree_skips_node_modules_next_and_dotfiles(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        app = get_settings().runs_dir / run_id / "app"
        for rel in (
            "package.json",
            "app/page.tsx",
            "app/kit/product.css",
            "components/Nav.tsx",
            "node_modules/react/index.js",
            ".next/server/x.js",
            ".env",
            ".gitignore",
            "app/.hidden/a.ts",
        ):
            write(app, rel)
        res = client.get(FILES.format(run_id))
        assert res.status_code == 200
        tree = res.json()
        assert names(tree) == ["app", "components", "package.json"]  # dirs first, then files
        app_node = tree[0]
        assert app_node["type"] == "dir" and app_node["path"] == "app"
        assert names(app_node["children"]) == ["kit", "page.tsx"]
        assert app_node["children"][0]["children"][0]["path"] == "app/kit/product.css"
        assert tree[2]["type"] == "file" and tree[2]["children"] is None


def test_file_tree_depth_is_capped_at_six(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        app = get_settings().runs_dir / run_id / "app"
        write(app, "a/b/c/d/e/f/g/deep.txt")
        node = client.get(FILES.format(run_id)).json()[0]
        depth = 1
        while node["children"]:
            node = node["children"][0]
            depth += 1
        assert node["name"] == "f" and depth == 6  # g and the file are beyond the cap


def test_files_and_build_404_for_unknown_run_and_no_app(client_for) -> None:
    with client_for() as client:
        assert client.get(FILES.format("r_000000")).status_code == 404
        assert client.get(BUILD.format("r_000000")).status_code == 404
        run_id = create_run(client)
        assert client.get(FILES.format(run_id)).status_code == 404
        assert client.get(BUILD.format(run_id)).status_code == 404


def test_traversal_is_impossible_there_is_no_path_input(client_for) -> None:
    with client_for() as client:
        assert client.get("/api/runs/..%2f..%2fetc/files").status_code == 404
        run_id = create_run(client)
        app = get_settings().runs_dir / run_id / "app"
        write(app, "ok.txt")
        write(app.parent, "secret.txt", "nope")
        res = client.get(FILES.format(run_id), params={"path": ".."})
        assert names(res.json()) == ["ok.txt"]


def test_build_returns_build_json(client_for) -> None:
    with client_for() as client:
        run_id = create_run(client)
        info = {
            "ok": False,
            "duration_s": 3.2,
            "attempts": 3,
            "error": {"file": "app/page.tsx", "line": 4},
            "log_tail": "boom",
        }
        write(get_settings().runs_dir / run_id, "build.json", json.dumps(info))
        res = client.get(BUILD.format(run_id))
        assert res.status_code == 200 and res.json() == info


def test_preview_409_until_built_then_redirects_to_the_direct_url(client_for) -> None:
    with client_for() as client:
        assert client.post(PREVIEW.format("r_000000")).status_code == 404
        run_id = create_run(client)
        wait_status(client, run_id, "waiting_gate1")
        assert client.post(PREVIEW.format(run_id)).status_code == 409
        run_dir = get_settings().runs_dir / run_id
        write(run_dir, "build.json", json.dumps({"ok": False}))
        assert client.post(PREVIEW.format(run_id)).status_code == 409

        async def fake_ensure(rid: str) -> int:
            return 4321

        client.app.state.preview.ensure = fake_ensure  # type: ignore[attr-defined]
        write(run_dir, "build.json", json.dumps({"ok": True}))
        body = client.post(PREVIEW.format(run_id)).json()
        assert body == {"url": "http://127.0.0.1:4321/", "port": 4321}
        res = client.get(PREVIEW.format(run_id) + "/dispatch?tab=1", follow_redirects=False)
        assert res.status_code == 307
        assert res.headers["location"] == "http://127.0.0.1:4321/dispatch?tab=1"
        assert client.head(PREVIEW.format(run_id) + "/", follow_redirects=False).status_code == 307
