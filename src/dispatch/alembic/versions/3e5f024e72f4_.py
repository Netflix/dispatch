"""Deletes participant roles with null participant id foreign key

Revision ID: 3e5f024e72f4
Revises: 47d04a78a9e4
Create Date: 2021-05-24 12:12:03.879035

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "3e5f024e72f4"
down_revision = "47d04a78a9e4"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    bind.execute("DELETE FROM participant_role WHERE participant_id is NULL")


def downgrade():
    pass
