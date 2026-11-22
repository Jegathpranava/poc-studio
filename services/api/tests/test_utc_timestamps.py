"""SQLite drops the UTC offset; the API must still return offset-aware timestamps.

Without this the browser showed '5 h ago' for a new run in IST.
"""

from datetime import UTC, datetime

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from poc_studio.db.base import Base
from poc_studio.db.models import Project


def test_timestamps_come_back_as_utc() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    with Session(engine) as s:
        s.add(Project(client_name="Acme", client_name_key="acme"))
        s.commit()
    with Session(engine) as s:
        p = s.scalars(select(Project)).one()
        assert p.created_at.tzinfo is not None
        assert abs((datetime.now(UTC) - p.created_at).total_seconds()) < 60
