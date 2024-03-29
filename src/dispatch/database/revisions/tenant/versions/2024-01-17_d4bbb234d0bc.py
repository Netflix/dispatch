"""Adds service column to forms

Revision ID: d4bbb234d0bc
Revises: 065c59f15267
Create Date: 2024-01-17 09:45:33.493774

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "d4bbb234d0bc"
down_revision = "065c59f15267"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("forms_type", sa.Column("service_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "forms_type", "service", ["service_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "forms_type", type_="foreignkey")
    op.drop_column("forms_type", "service_id")
    # ### end Alembic commands ###
