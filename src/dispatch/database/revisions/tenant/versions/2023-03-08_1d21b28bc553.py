"""Adds ondelete cascade to case table for participant FK

Revision ID: 1d21b28bc553
Revises: 1ded4c2a7801
Create Date: 2023-03-08 10:26:05.472740

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "1d21b28bc553"
down_revision = "1ded4c2a7801"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("case_assignee_id_fkey", "case", type_="foreignkey")
    op.create_foreign_key(None, "case", "participant", ["assignee_id"], ["id"], ondelete="CASCADE")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "case", type_="foreignkey")
    op.create_foreign_key("case_assignee_id_fkey", "case", "participant", ["assignee_id"], ["id"])
    # ### end Alembic commands ###
