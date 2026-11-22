"""Client share tokens: 24 random bytes, URL-safe, stored as a sha256 hash, valid for 30 days."""

import hashlib
import secrets
from collections.abc import Callable
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from poc_studio.db.models import ShareToken

TOKEN_BYTES = 24
TTL_DAYS = 30


def _utcnow() -> datetime:
    return datetime.now(UTC)


clock: Callable[[], datetime] = _utcnow  # tests replace this with a fake clock


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_token(session: Session, run_id: str) -> tuple[str, datetime]:
    token = secrets.token_urlsafe(TOKEN_BYTES)
    expires = clock() + timedelta(days=TTL_DAYS)
    session.add(
        ShareToken(run_id=run_id, token_hash=hash_token(token), created_at=clock(), expires_at=expires)
    )
    session.commit()
    return token, expires


def resolve_token(session: Session, token: str) -> ShareToken | None:
    """The row for a valid, unexpired token, else None."""
    if not token or len(token) > 100:
        return None
    row = session.scalar(select(ShareToken).where(ShareToken.token_hash == hash_token(token)))
    if row is None or row.expires_at <= clock():
        return None
    return row
