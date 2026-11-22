"""artifacts: allow the `repo` type (the publish result written by the repo node)

Revision ID: 0005
Revises: 0004
Create Date: 2026-11-23 09:00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0005"
down_revision: str | Sequence[str] | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

BEFORE = "'requirements', 'architecture', 'prototype', 'deck', 'pptx', 'video', 'docs', 'qa_report', 'share_export', 'screenpack'"
AFTER = BEFORE + ", 'repo'"


def _swap(types: str) -> None:
    with op.batch_alter_table("artifacts", schema=None) as batch_op:
        batch_op.drop_constraint("ck_artifacts_type", type_="check")
        batch_op.create_check_constraint("ck_artifacts_type", f"type IN ({types})")


def upgrade() -> None:
    _swap(AFTER)


def downgrade() -> None:
    op.execute("DELETE FROM artifacts WHERE type = 'repo'")
    _swap(BEFORE)
