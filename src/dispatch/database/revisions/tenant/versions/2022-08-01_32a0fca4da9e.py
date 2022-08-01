"""Removes ondelete cascade for case_id in the incident data model

Revision ID: 32a0fca4da9e
Revises: 391f7c3e6992
Create Date: 2022-08-01 14:49:26.492323

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "32a0fca4da9e"
down_revision = "391f7c3e6992"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("incident_case_id_fkey", "incident", type_="foreignkey")
    op.create_foreign_key(None, "incident", "case", ["case_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "incident", type_="foreignkey")
    op.create_foreign_key(
        "incident_case_id_fkey", "incident", "case", ["case_id"], ["id"], ondelete="CASCADE"
    )
    # ### end Alembic commands ###
