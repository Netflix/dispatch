"""This drops old un-needed tables

Revision ID: 22ee48df12a0
Revises: efe949b0fe55
Create Date: 2021-04-22 15:08:50.415491

"""
from alembic import op

# TODO add to the revision history later for cleanup
# revision identifiers, used by Alembic.
revision = "22ee48df12a0"
down_revision = "efe949b0fe55"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("service_terms")
    op.drop_table("recommendation_incident_priorities")
    op.drop_table("service_incident_priority")
    op.drop_table("document_terms")
    op.drop_table("assoc_individual_contact_incident_priority")
    op.drop_table("recommendation_individual_contacts")
    op.drop_table("team_contact_incident_priority")
    op.drop_table("recommendation_incident_types")
    op.drop_table("recommendation_documents")
    op.drop_table("team_contact_incident_type")
    op.drop_table("recommendation_services")
    op.drop_table("recommendation_accuracy")
    op.drop_table("recommendation_team_contacts")
    op.drop_table("document_incident_priority")
    op.drop_table("document_incident_type")
    op.drop_table("recommendation_terms")
    op.drop_table("assoc_individual_contact_terms")
    op.drop_table("assoc_individual_contact_incident_type")
    op.drop_table("team_contact_terms")
    op.drop_table("service_incident_type")
    op.drop_column("recommendation", "text")


def downgrade():
    pass
