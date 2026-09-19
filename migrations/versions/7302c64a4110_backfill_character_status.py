"""backfill existing characters to active status

Revision ID: 7302c64a4110
Revises: 12031ced9f76
Create Date: 2026-09-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "7302c64a4110"
down_revision: Union[str, Sequence[str], None] = "12031ced9f76"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Characters created before the public character list existed were left in
    # "draft" status (the model default) and so never show up in GET /characters/.
    # Anyone's characters should be chattable by anyone, so make them all active.
    op.execute("UPDATE characters SET status = 'active' WHERE status != 'active'")


def downgrade() -> None:
    # The original per-row status values weren't recorded anywhere, so this
    # can't be un-done precisely. Left as a no-op rather than guessing.
    pass
