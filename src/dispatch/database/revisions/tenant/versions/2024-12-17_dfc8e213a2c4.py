"""Adds conversation target and oncall service override options to signal instances

Revision ID: dfc8e213a2c4
Revises: 2d9e4d392ea4
Create Date: 2024-12-17 10:02:26.920568

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dfc8e213a2c4'
down_revision = '2d9e4d392ea4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("signal_instance", sa.Column("conversation_target", sa.String(), nullable=True))
    op.add_column("signal_instance", sa.Column("oncall_service_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "oncall_service_id_fkey",
        "signal_instance",
        "service",
        ["oncall_service_id"],
        ["id"]
    )


def downgrade():
    op.drop_constraint("oncall_service_id_fkey", "signal_instance", type_="foreignkey")
    op.drop_column("signal_instance", "oncall_service_id")
    op.drop_column("signal_instance", "conversation_target")
