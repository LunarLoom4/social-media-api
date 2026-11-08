"""Add Foreign Key to the 'posts' table.

Revision ID: 929292d76d13
Revises: dbf1ce59871b
Create Date: 2026-11-05 10:15:14.352776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '929292d76d13'
down_revision: Union[str, Sequence[str], None] = 'dbf1ce59871b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        "posts",
        sa.Column("owner_id", sa.Integer(), nullable = False)
    )

    op.create_foreign_key(
        "posts_owner_id_fkey",
        source_table = "posts",
        referent_table = "users",
        local_cols = ["owner_id"],
        remote_cols = ["id"],
        ondelete = "CASCADE"
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint("posts_owner_id_fkey", table_name = "posts")
    op.drop_column("posts", "owner_id")
    pass
