"""Adds an environment variable for spliting up test and prod signals.

Revision ID: 1dd78f49e303
Revises: 4e57f5b1f3f3
Create Date: 2023-09-05 09:57:18.160124

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "1dd78f49e303"
down_revision = "4e57f5b1f3f3"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("signal", sa.Column("environment", sa.String(), nullable=True, default="prod"))
    op.execute("UPDATE signal SET environment = 'prod'")
    op.alter_column("signal", "environment", nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("signal", "environment")
    # ### end Alembic commands ###
