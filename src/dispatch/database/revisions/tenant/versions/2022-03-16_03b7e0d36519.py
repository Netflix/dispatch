"""Adds default column to dispatch user project table

Revision ID: 03b7e0d36519
Revises: b5d3706a1d54
Create Date: 2022-03-16 09:35:00.406534

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "03b7e0d36519"
down_revision = "b5d3706a1d54"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("dispatch_user_project", sa.Column("default", sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("dispatch_user_project", "default")
    # ### end Alembic commands ###
