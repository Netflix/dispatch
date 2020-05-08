"""Adds a data model for incident updates

Revision ID: e14760d2a20f
Revises: 734feb50c4ce
Create Date: 2020-05-08 14:24:07.022944

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e14760d2a20f"
down_revision = "734feb50c4ce"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "incident_update",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("overview", sa.String(), nullable=True),
        sa.Column("current_status", sa.String(), nullable=True),
        sa.Column("next_steps", sa.String(), nullable=True),
        sa.Column("incident_id", sa.Integer(), nullable=True),
        sa.Column("participant_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["incident_id"], ["incident.id"]),
        sa.ForeignKeyConstraint(["participant_id"], ["participant.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("document", sa.Column("incident_update_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "document", "incident_update", ["incident_update_id"], ["id"])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "document", type_="foreignkey")
    op.drop_column("document", "incident_update_id")
    op.drop_table("incident_update")
    # ### end Alembic commands ###
