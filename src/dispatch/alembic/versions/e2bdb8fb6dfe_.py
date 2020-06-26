"""Merge versions

Revision ID: e2bdb8fb6dfe
Revises: 86f99b17b421, 57b023382626
Create Date: 2020-06-24 16:15:00.971514

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e2bdb8fb6dfe"
down_revision = ("86f99b17b421", "57b023382626")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
