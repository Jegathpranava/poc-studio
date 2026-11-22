"""approvals.note and approvals.consumed_at, so a decision lost to a crash is replayed on restart

Revision ID: 0003
Revises: 0002
Create Date: 2026-11-22 21:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0003"
down_revision: str | Sequence[str] | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("approvals", schema=None) as batch_op:
        batch_op.add_column(sa.Column("note", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("approvals", schema=None) as batch_op:
        batch_op.drop_column("consumed_at")
        batch_op.drop_column("note")
