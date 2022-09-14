"""Adds more signal fields

Revision ID: f6d06be90637
Revises: b3483f267646
Create Date: 2022-09-13 09:57:19.743385

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "f6d06be90637"
down_revision = "b3483f267646"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("signal", sa.Column("external_url", sa.String(), nullable=True))
    op.add_column("signal", sa.Column("external_id", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("signal", "external_id")
    op.drop_column("signal", "external_url")
    # ### end Alembic commands ###
