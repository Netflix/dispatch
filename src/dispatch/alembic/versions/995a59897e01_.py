"""Allows plugins to be disable.

Revision ID: 995a59897e01
Revises: 72c7fa0ce0a3
Create Date: 2020-09-24 10:08:07.729599

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "995a59897e01"
down_revision = "72c7fa0ce0a3"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("workflow", sa.Column("enabled", sa.Boolean(), nullable=True))
    op.drop_column("workflow", "is_active")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "workflow", sa.Column("is_active", sa.BOOLEAN(), autoincrement=False, nullable=True)
    )
    op.drop_column("workflow", "enabled")
    # ### end Alembic commands ###
