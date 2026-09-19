"""add password hash to users

Revision ID: 7d0148a85b24
Revises: 7d53229252a2
Create Date: 2026-08-20 07:16:18.406250
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7d0148a85b24"
down_revision: Union[str, Sequence[str], None] = "7d53229252a2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=True,
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "users",
        "password_hash",
    )