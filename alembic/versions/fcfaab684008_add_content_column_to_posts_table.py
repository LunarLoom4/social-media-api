"""Add 'content' column to 'posts' table.

Revision ID: fcfaab684008
Revises: efbc9061e7ef
Create Date: 2026-11-05 04:01:30.917215

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fcfaab684008'
down_revision: Union[str, Sequence[str], None] = 'efbc9061e7ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "posts",
        sa.Column("content", sa.String(), nullable = False)
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("posts", "content")
    pass
