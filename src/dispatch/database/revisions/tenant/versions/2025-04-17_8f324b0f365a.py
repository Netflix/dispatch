"""Adds `event` column to differentiate if the case was reported via the event reporting form

Revision ID: 8f324b0f365a
Revises: 4aa819afb065
Create Date: 2025-04-17 11:52:11.148817

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "8f324b0f365a"
down_revision = "4aa819afb065"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("case", sa.Column("event", sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column("case", "event")
