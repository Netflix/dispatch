"""Adds email search.

Revision ID: d1b5ed66d83d
Revises: 1dafcb9ad889
Create Date: 2023-03-27 08:57:44.499535

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.schema import MetaData

from dispatch.search.fulltext import sync_trigger


# revision identifiers, used by Alembic.
revision = "d1b5ed66d83d"
down_revision = "1dafcb9ad889"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_context().connection
    metadata = MetaData(schema=conn.dialect.default_schema_name)
    metadata.bind = conn
    table = sa.Table("individual_contact", metadata, autoload_with=conn)
    sync_trigger(conn, table, "search_vector", ["name", "title", "email", "company", "notes"])


def downgrade():
    pass
