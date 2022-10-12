"""Adds signal instance

Revision ID: af5a185d8ddc
Revises: 534c316ba65b
Create Date: 2022-10-11 10:06:15.458809

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "af5a185d8ddc"
down_revision = "534c316ba65b"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("signal")
    op.create_table(
        "signal",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("owner", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("external_url", sa.String(), nullable=True),
        sa.Column("external_id", sa.String(), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("variant", sa.String(), nullable=True),
        sa.Column("case_type_id", sa.Integer(), nullable=True),
        sa.Column("search_vector", sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["case_type_id"],
            ["case_type.id"],
        ),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["source_id"],
            ["source.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "signal_search_vector_idx",
        "signal",
        ["search_vector"],
        unique=False,
        postgresql_using="gin",
    )
    op.create_table(
        "signal_instance",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("case_id", sa.Integer(), nullable=True),
        sa.Column("signal_id", sa.Integer(), nullable=True),
        sa.Column("fingerprint", sa.String(), nullable=True),
        sa.Column("severity", sa.String(), nullable=True),
        sa.Column("raw", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["case_id"],
            ["case.id"],
        ),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["signal_id"],
            ["signal.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "assoc_duplication_rule_tag_types",
        sa.Column("duplication_rule_id", sa.Integer(), nullable=False),
        sa.Column("tag_type_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["duplication_rule_id"], ["duplication_rule.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["tag_type_id"], ["tag_type.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("duplication_rule_id", "tag_type_id"),
    )
    op.create_table(
        "assoc_signal_instance_tags",
        sa.Column("signal_instance_id", postgresql.UUID(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["signal_instance_id"], ["signal_instance.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("signal_instance_id", "tag_id"),
    )
    op.create_table(
        "assoc_suppression_rule_tags",
        sa.Column("suppression_rule_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["suppression_rule_id"], ["suppression_rule.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("suppression_rule_id", "tag_id"),
    )
    op.add_column("duplication_rule", sa.Column("signal_id", sa.Integer(), nullable=True))
    op.add_column("duplication_rule", sa.Column("window", sa.Integer(), nullable=True))
    op.drop_constraint("duplication_rule_name_project_id_key", "duplication_rule", type_="unique")
    op.drop_index("duplication_rule_search_vector_idx", table_name="duplication_rule")
    op.create_foreign_key(None, "duplication_rule", "signal", ["signal_id"], ["id"])
    op.drop_column("duplication_rule", "search_vector")
    op.drop_column("duplication_rule", "expression")
    op.drop_column("duplication_rule", "name")
    op.drop_column("duplication_rule", "description")
    op.add_column("suppression_rule", sa.Column("signal_id", sa.Integer(), nullable=True))
    op.drop_constraint("suppression_rule_name_project_id_key", "suppression_rule", type_="unique")
    op.drop_index("suppression_rule_search_vector_idx", table_name="suppression_rule")
    op.create_foreign_key(None, "suppression_rule", "signal", ["signal_id"], ["id"])
    op.drop_column("suppression_rule", "search_vector")
    op.drop_column("suppression_rule", "expression")
    op.drop_column("suppression_rule", "name")
    op.drop_column("suppression_rule", "description")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "suppression_rule",
        sa.Column("description", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "suppression_rule", sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "suppression_rule",
        sa.Column(
            "expression",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "suppression_rule",
        sa.Column("search_vector", postgresql.TSVECTOR(), autoincrement=False, nullable=True),
    )
    op.drop_constraint(None, "suppression_rule", type_="foreignkey")
    op.create_index(
        "suppression_rule_search_vector_idx", "suppression_rule", ["search_vector"], unique=False
    )
    op.create_unique_constraint(
        "suppression_rule_name_project_id_key", "suppression_rule", ["name", "project_id"]
    )
    op.drop_column("suppression_rule", "signal_id")
    op.add_column(
        "duplication_rule",
        sa.Column("description", sa.VARCHAR(), autoincrement=False, nullable=True),
    )
    op.add_column(
        "duplication_rule", sa.Column("name", sa.VARCHAR(), autoincrement=False, nullable=True)
    )
    op.add_column(
        "duplication_rule",
        sa.Column(
            "expression",
            postgresql.JSON(astext_type=sa.Text()),
            autoincrement=False,
            nullable=False,
        ),
    )
    op.add_column(
        "duplication_rule",
        sa.Column("search_vector", postgresql.TSVECTOR(), autoincrement=False, nullable=True),
    )
    op.drop_constraint(None, "duplication_rule", type_="foreignkey")
    op.create_index(
        "duplication_rule_search_vector_idx", "duplication_rule", ["search_vector"], unique=False
    )
    op.create_unique_constraint(
        "duplication_rule_name_project_id_key", "duplication_rule", ["name", "project_id"]
    )
    op.drop_column("duplication_rule", "window")
    op.drop_column("duplication_rule", "signal_id")
    op.drop_table("assoc_suppression_rule_tags")
    op.drop_table("assoc_signal_instance_tags")
    op.drop_table("assoc_duplication_rule_tag_types")
    op.drop_table("signal_instance")
    op.drop_index("signal_search_vector_idx", table_name="signal", postgresql_using="gin")
    op.drop_table("signal")
    # ### end Alembic commands ###
