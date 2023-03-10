"""Adds missing tag search columns

Revision ID: 7db13bf5c5d7
Revises: ec78c132ab93
Create Date: 2023-03-09 16:31:22.963497

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import MetaData

from dispatch.search.fulltext import sync_trigger


# revision identifiers, used by Alembic.
revision = "7db13bf5c5d7"
down_revision = "ec78c132ab93"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_context().connection
    metadata = MetaData(bind=conn, schema=conn.dialect.default_schema_name)
    table = sa.Table("tag", metadata, autoload=True)
    sync_trigger(conn, table, "search_vector", ["name", "description", "external_id"])


def downgrade():
    pass
