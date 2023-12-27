"""empty message

Revision ID: ed0b0388fa3f
Revises: 5c60513d6e5e
Create Date: 2023-12-27 13:44:17.960851

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = "ed0b0388fa3f"
down_revision = "5c60513d6e5e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "plugin_event",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("slug", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("plugin_id", sa.Integer(), nullable=True),
        sa.Column("search_vector", sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True),
        sa.ForeignKeyConstraint(
            ["plugin_id"],
            ["dispatch_core.plugin.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug"),
        schema="dispatch_core",
    )
    op.create_index(
        "plugin_event_search_vector_idx",
        "plugin_event",
        ["search_vector"],
        unique=False,
        schema="dispatch_core",
        postgresql_using="gin",
    )
    op.drop_constraint(
        "dispatch_user_organization_dispatch_user_id_fkey",
        "dispatch_user_organization",
        type_="foreignkey",
    )
    op.drop_constraint(
        "dispatch_user_organization_organization_id_fkey",
        "dispatch_user_organization",
        type_="foreignkey",
    )
    op.create_foreign_key(
        None,
        "dispatch_user_organization",
        "organization",
        ["organization_id"],
        ["id"],
        source_schema="dispatch_core",
        referent_schema="dispatch_core",
    )
    op.create_foreign_key(
        None,
        "dispatch_user_organization",
        "dispatch_user",
        ["dispatch_user_id"],
        ["id"],
        source_schema="dispatch_core",
        referent_schema="dispatch_core",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(
        None, "dispatch_user_organization", schema="dispatch_core", type_="foreignkey"
    )
    op.drop_constraint(
        None, "dispatch_user_organization", schema="dispatch_core", type_="foreignkey"
    )
    op.create_foreign_key(
        "dispatch_user_organization_organization_id_fkey",
        "dispatch_user_organization",
        "organization",
        ["organization_id"],
        ["id"],
    )
    op.create_foreign_key(
        "dispatch_user_organization_dispatch_user_id_fkey",
        "dispatch_user_organization",
        "dispatch_user",
        ["dispatch_user_id"],
        ["id"],
    )
    op.drop_index(
        "plugin_event_search_vector_idx",
        table_name="plugin_event",
        schema="dispatch_core",
        postgresql_using="gin",
    )
    op.drop_table("plugin_event", schema="dispatch_core")
    # ### end Alembic commands ###
