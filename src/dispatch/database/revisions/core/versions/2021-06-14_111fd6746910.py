"""empty message

Revision ID: 111fd6746910
Revises: f011c050b9ba
Create Date: 2021-06-14 09:46:38.125195

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "111fd6746910"
down_revision = "f011c050b9ba"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "dispatch_user_organization", "dispatch_user_id", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "dispatch_user_organization", "organization_id", existing_type=sa.INTEGER(), nullable=False
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
    op.drop_column("dispatch_user_organization", "id")
    op.add_column("organization", sa.Column("banner_enabled", sa.Boolean(), nullable=True))
    op.add_column("organization", sa.Column("banner_color", sa.String(), nullable=True))
    op.add_column("organization", sa.Column("banner_text", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("organization", "banner_text")
    op.drop_column("organization", "banner_color")
    op.drop_column("organization", "banner_enabled")
    op.add_column(
        "dispatch_user_organization",
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text("nextval('public.dispatch_user_organization_id_seq'::regclass)"),
            autoincrement=True,
            nullable=False,
        ),
    )
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
        referent_schema="public",
    )
    op.create_foreign_key(
        "dispatch_user_organization_dispatch_user_id_fkey",
        "dispatch_user_organization",
        "dispatch_user",
        ["dispatch_user_id"],
        ["id"],
        referent_schema="public",
    )
    op.alter_column(
        "dispatch_user_organization", "organization_id", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "dispatch_user_organization", "dispatch_user_id", existing_type=sa.INTEGER(), nullable=True
    )
    # ### end Alembic commands ###
