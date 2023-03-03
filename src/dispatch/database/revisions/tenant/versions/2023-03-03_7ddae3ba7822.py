"""Adds signal triggers

Revision ID: 7ddae3ba7822
Revises: 65db2acae3ea
Create Date: 2023-03-03 10:16:57.890859

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import MetaData

from dispatch.search.fulltext import sync_trigger

# revision identifiers, used by Alembic.
revision = "7ddae3ba7822"
down_revision = "65db2acae3ea"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_context().connection
    metadata = MetaData(bind=conn, schema=conn.dialect.default_schema_name)
    table = sa.Table("signal", metadata, autoload=True)
    sync_trigger(conn, table, "search_vector", ["name", "description", "variant"])


def downgrade():
    pass
