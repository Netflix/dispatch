"""Adds reminders to oncall shift feedback

Revision ID: 0560fab4537f
Revises: 1dd78f49e303
Create Date: 2023-09-08 17:13:57.903367

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "0560fab4537f"
down_revision = "1dd78f49e303"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table("service_feedback_reminder",
    sa.Column("id", sa.Integer(), nullable=False),
    sa.Column("reminder_at", sa.DateTime(), nullable=True),
    sa.Column("schedule_id", sa.String(), nullable=True),
    sa.Column("schedule_name", sa.String(), nullable=True),
    sa.Column("shift_end_at", sa.DateTime(), nullable=True),
    sa.Column("individual_contact_id", sa.Integer(), nullable=True),
    sa.Column("project_id", sa.Integer(), nullable=True),
    sa.Column("created_at", sa.DateTime(), nullable=True),
    sa.Column("updated_at", sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(["individual_contact_id"], ["individual_contact.id"], ),
    sa.ForeignKeyConstraint(["project_id"], ["project.id"], ),
    sa.PrimaryKeyConstraint("id")
    )
    op.add_column("service_feedback", sa.Column("reminder_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "service_feedback", "service_feedback_reminder", ["reminder_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "service_feedback", type_="foreignkey")
    op.drop_column("service_feedback", "reminder_id")
    op.drop_table("service_feedback_reminder")
    # ### end Alembic commands ###
