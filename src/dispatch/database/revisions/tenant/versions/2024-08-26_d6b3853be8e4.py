"""Adding column for select_commander_visibility

Revision ID: d6b3853be8e4
Revises: 71cd7ed999c4
Create Date: 2024-08-26 14:42:48.423369

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'd6b3853be8e4'
down_revision = '71cd7ed999c4'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('project', sa.Column('select_commander_visibility', sa.Boolean(), server_default='t', nullable=True))

def downgrade():
    op.drop_column('project', 'select_commander_visibility')
