"""Ensure search expression is not null

Revision ID: ceaf01079f4f
Revises: 3820a792d88a
Create Date: 2021-10-05 14:01:53.423667

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "ceaf01079f4f"
down_revision = "3820a792d88a"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("UPDATE search_filter SET expression = '[]' WHERE expression is null")
    op.alter_column("search_filter", "expression", nullable=False)


def downgrade():
    op.alter_column("search_filter", "expression", nullable=True)
