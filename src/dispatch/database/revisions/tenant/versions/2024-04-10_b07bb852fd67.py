"""Adds attorney form schema and scoring schema to forms type

Revision ID: b07bb852fd67
Revises: 71cb25c06fa0
Create Date: 2024-04-10 15:51:10.914748

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "b07bb852fd67"
down_revision = "71cb25c06fa0"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("forms_type", sa.Column("attorney_form_schema", sa.String(), nullable=True))
    op.add_column("forms_type", sa.Column("scoring_schema", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("forms_type", "scoring_schema")
    op.drop_column("forms_type", "attorney_form_schema")
    # ### end Alembic commands ###
