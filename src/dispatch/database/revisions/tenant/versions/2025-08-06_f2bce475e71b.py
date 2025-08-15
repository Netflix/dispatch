"""Adds support for configuring security event suggestions in the project model.

Revision ID: f2bce475e71b
Revises: 408118048599
Create Date: 2025-08-06 09:48:16.045362

"""
from alembic import op
import sqlalchemy as sa


revision = 'f2bce475e71b'
down_revision = '4649b11b683f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('project', sa.Column('suggest_security_event_over_incident', sa.Boolean(), server_default='t', nullable=True))


def downgrade():
    op.drop_column('project', 'suggest_security_event_over_incident')
