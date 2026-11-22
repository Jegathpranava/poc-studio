"""Run the API with the Task 20 routers included (until `main.py` calls `include_extra` itself)."""

import sys
from pathlib import Path

import uvicorn

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # package root

from poc_studio.extra_routes import include_extra, on_startup  # noqa: E402
from poc_studio.main import create_app  # noqa: E402

app = create_app()
include_extra(app)

if __name__ == "__main__":
    on_startup()
    uvicorn.run(app, host="127.0.0.1", port=8000)
