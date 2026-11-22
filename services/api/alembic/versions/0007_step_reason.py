"""agent_steps.reason: why a rerun started (revise, send_back or retry)

Revision ID: 0007
Revises: 0006
Create Date: 2026-11-23 18:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "0007"
down_revision: str | Sequence[str] | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("agent_steps", schema=None) as batch_op:
        batch_op.add_column(sa.Column("reason", sa.String(20), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("agent_steps", schema=None) as batch_op:
        batch_op.drop_column("reason")
