"""add character avatar

Revision ID: 12031ced9f76
Revises: 7d53229252a2
Create Date: 2026-09-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "12031ced9f76"
down_revision: Union[str, Sequence[str], None] = "7d0148a85b24"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "characters",
        sa.Column("avatar_url", sa.String(length=500), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("characters", "avatar_url")
