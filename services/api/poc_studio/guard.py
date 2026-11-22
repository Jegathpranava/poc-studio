"""Local API hardening: a browser page on another origin must not be able to drive this API.

Unsafe methods on `/api/*` need a JSON or multipart body (a cross-site `<form>` or a simple `fetch` can only
send urlencoded, multipart-without-CORS or text/plain) and, when the browser says where it came from, the
web app's own origin. Requests with no `Origin` header (curl, the test client, server-side fetches) pass.
"""

import json

from starlette.types import ASGIApp, Receive, Scope, Send

APP_ORIGINS = frozenset({"http://127.0.0.1:3000", "http://localhost:3000"})
UNSAFE_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
BODY_TYPES = ("application/json", "multipart/form-data")


class UnsafeRequestGuard:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] == "http"
            and scope["method"] in UNSAFE_METHODS
            and scope["path"].startswith("/api/")
        ):
            headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope["headers"]}
            origin = headers.get("origin")
            if origin is not None:
                ctype = headers.get("content-type", "").split(";")[0].strip().lower()
                if origin not in APP_ORIGINS or ctype not in BODY_TYPES:
                    await _forbidden(send)
                    return
        await self.app(scope, receive, send)


async def _forbidden(send: Send) -> None:
    body = json.dumps({"detail": "This request is not allowed from here."}).encode()
    await send(
        {
            "type": "http.response.start",
            "status": 403,
            "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())],
        }
    )
    await send({"type": "http.response.body", "body": body})
