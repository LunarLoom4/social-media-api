"""Add 'published' and 'created_at' to the 'posts' table.

Revision ID: 7853ac40991a
Revises: 929292d76d13
Create Date: 2026-11-05 10:29:01.634111

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7853ac40991a'
down_revision: Union[str, Sequence[str], None] = '929292d76d13'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "posts",
        sa.Column("published", sa.Boolean(), nullable = False, server_default = "TRUE")
    )
    op.add_column(
        "posts",
        sa.Column("created_at", sa.TIMESTAMP(timezone = True), nullable = False, server_default = sa.text("NOW()"))
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column("posts", "published")
    op.drop_column("posts", "created_at")
    pass
