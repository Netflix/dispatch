"""empty message

Revision ID: 15a8d3228123
Revises: 4286dcce0a2d
Create Date: 2024-06-28 11:19:27.227089

"""

from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = "15a8d3228123"
down_revision = "4286dcce0a2d"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "case_cost_type",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("category", sa.String(), nullable=True),
        sa.Column("details", sqlalchemy_utils.types.json.JSONType(), nullable=True),
        sa.Column("default", sa.Boolean(), nullable=True),
        sa.Column("editable", sa.Boolean(), nullable=True),
        sa.Column("search_vector", sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "case_cost_type_search_vector_idx",
        "case_cost_type",
        ["search_vector"],
        unique=False,
        postgresql_using="gin",
    )
    op.create_table(
        "case_cost",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=True),
        sa.Column("case_cost_type_id", sa.Integer(), nullable=True),
        sa.Column("case_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["case_cost_type_id"],
            ["case_cost_type.id"],
        ),
        sa.ForeignKeyConstraint(["case_id"], ["case.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("case_type", sa.Column("cost_model_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "case_type", "cost_model", ["cost_model_id"], ["id"])
    op.add_column("participant_activity", sa.Column("case_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "participant_activity", "case", ["case_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "participant_activity", type_="foreignkey")
    op.drop_column("participant_activity", "case_id")
    op.drop_constraint(None, "case_type", type_="foreignkey")
    op.drop_column("case_type", "cost_model_id")
    op.drop_table("case_cost")
    op.drop_index(
        "case_cost_type_search_vector_idx", table_name="case_cost_type", postgresql_using="gin"
    )
    op.drop_table("case_cost_type")
    # ### end Alembic commands ###
