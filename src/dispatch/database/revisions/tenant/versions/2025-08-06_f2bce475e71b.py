"""Adds support for configuring the reporting security incidents in the project model.

Revision ID: f2bce475e71b
Revises: 408118048599
Create Date: 2025-08-06 09:48:16.045362

"""
from alembic import op
import sqlalchemy as sa


revision = 'f2bce475e71b'
down_revision = '408118048599'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('project', sa.Column('show_report_incident_button', sa.Boolean(), server_default='t', nullable=True))


def downgrade():
    op.drop_column('project', 'show_report_incident_button')
