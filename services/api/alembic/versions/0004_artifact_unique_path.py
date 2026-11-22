"""artifacts: unique (run_id, path), so two writers cannot save the same version of a file

Revision ID: 0004
Revises: 0003
Create Date: 2026-11-22 23:00:00
"""

from collections.abc import Sequence

from alembic import op

revision: str = "0004"
down_revision: str | Sequence[str] | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("artifacts", schema=None) as batch_op:
        batch_op.create_unique_constraint("uq_artifacts_run_path", ["run_id", "path"])


def downgrade() -> None:
    with op.batch_alter_table("artifacts", schema=None) as batch_op:
        batch_op.drop_constraint("uq_artifacts_run_path", type_="unique")
