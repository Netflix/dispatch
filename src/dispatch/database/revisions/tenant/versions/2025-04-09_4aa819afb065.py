"""Adds shift_hours_type column to service table

Revision ID: 4aa819afb065
Revises: bccbf255d6d1
Create Date: 2025-04-09 15:58:57.943940

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "4aa819afb065"
down_revision = "bccbf255d6d1"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "service", sa.Column("shift_hours_type", sa.Integer(), nullable=True, server_default="24")
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("service", "shift_hours_type")
    # ### end Alembic commands ###
