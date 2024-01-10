"""Adds cost model tables: cost_model, cost_model_activity, participant_activity

Revision ID: 065c59f15267
Revises: 99d317cbc848
Create Date: 2023-12-27 13:44:18.845443

"""
from alembic import op
import sqlalchemy as sa
import sqlalchemy_utils

# revision identifiers, used by Alembic.
revision = "065c59f15267"
down_revision = "99d317cbc848"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "cost_model",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.Column("search_vector", sqlalchemy_utils.types.ts_vector.TSVectorType(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", "project_id"),
    )
    op.create_index(
        "cost_model_search_vector_idx",
        "cost_model",
        ["search_vector"],
        unique=False,
        postgresql_using="gin",
    )
    op.create_table(
        "cost_model_activity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plugin_event_id", sa.Integer(), nullable=True),
        sa.Column("response_time_seconds", sa.Integer(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.ForeignKeyConstraint(
            ["plugin_event_id"], ["dispatch_core.plugin_event.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "assoc_cost_model_activities",
        sa.Column("cost_model_id", sa.Integer(), nullable=False),
        sa.Column("cost_model_activity_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["cost_model_activity_id"],
            ["cost_model_activity.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(["cost_model_id"], ["cost_model.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("cost_model_id", "cost_model_activity_id"),
    )
    op.create_table(
        "participant_activity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("plugin_event_id", sa.Integer(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=True),
        sa.Column("ended_at", sa.DateTime(), nullable=True),
        sa.Column("participant_id", sa.Integer(), nullable=True),
        sa.Column("incident_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["incident_id"],
            ["incident.id"],
        ),
        sa.ForeignKeyConstraint(
            ["participant_id"],
            ["participant.id"],
        ),
        sa.ForeignKeyConstraint(
            ["plugin_event_id"],
            ["dispatch_core.plugin_event.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column("incident", sa.Column("cost_model_id", sa.Integer(), nullable=True))
    op.create_foreign_key(None, "incident", "cost_model", ["cost_model_id"], ["id"])
    # # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, "incident", type_="foreignkey")
    op.drop_column("incident", "cost_model_id")
    op.drop_table("participant_activity")
    op.drop_table("assoc_cost_model_activities")
    op.drop_table("cost_model_activity")
    op.drop_index(
        "cost_model_search_vector_idx",
        table_name="cost_model",
        postgresql_using="gin",
    )
    op.drop_table("cost_model")
    # ### end Alembic commands ###
