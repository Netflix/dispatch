"""empty message

Revision ID: 5e03ddf1c8fa
Revises: e0d568f345c9
Create Date: 2022-02-11 11:21:22.645758

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "5e03ddf1c8fa"
down_revision = "e0d568f345c9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
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
        "dispatch_user",
        ["dispatch_user_id"],
        ["id"],
        source_schema="dispatch_core",
        referent_schema="dispatch_core",
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
    # ### end Alembic commands ###
