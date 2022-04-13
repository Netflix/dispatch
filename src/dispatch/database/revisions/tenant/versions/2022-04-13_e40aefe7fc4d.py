"""Adds column to incident priority model to allow for setting a color

Revision ID: e40aefe7fc4d
Revises: 03b7e0d36519
Create Date: 2022-04-13 09:44:48.400912

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "e40aefe7fc4d"
down_revision = "03b7e0d36519"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("incident_priority", sa.Column("color", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("incident_priority", "color")
    # ### end Alembic commands ###
