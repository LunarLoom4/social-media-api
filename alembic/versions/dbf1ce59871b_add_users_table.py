"""Add 'users' table.

Revision ID: dbf1ce59871b
Revises: fcfaab684008
Create Date: 2026-11-05 04:08:17.050748

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dbf1ce59871b'
down_revision: Union[str, Sequence[str], None] = 'fcfaab684008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable = False),
        sa.Column("email", sa.String(), nullable = False),
        sa.Column("password", sa.String(), nullable = False),
        sa.Column("created_at", sa.TIMESTAMP(timezone = True), nullable = False, server_default = sa.text('NOW()')),

        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email")
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_table("users")
    pass
