"""Migrates public data to default schema

Revision ID: ec00175489a1
Revises: 8bac2d09a067
Create Date: 2021-05-25 15:27:33.290421

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "ec00175489a1"
down_revision = "8bac2d09a067"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()

    # lets make our schema first
    sql = sa.text(
        """
        CREATE SCHEMA IF NOT EXISTS dispatch
        """
    )
    conn.execute(sql)

    sql = sa.text(
        """
        CREATE SCHEMA IF NOT EXISTS dispatch_organization_default
        """
    )
    conn.execute(sql)

    # copy data and structure from one table to another
    sql = """
        CREATE TABLE IF NOT EXISTS  {destination_table} AS SELECT * FROM {source_table}
        """
    # migrate common tables
    for source_table in ["organization", "dispatch_user"]:
        destination_table = f"dispatch.{source_table}"
        sql = sql.format(destination_table=destination_table, source_table=f"public.{source_table}")
        conn.execute(sa.text(sql))

    # migrate organization tables
    # for source_table in ["incident"]:
    #    destination_table = f"dispatch_organization_default.{source_table}"
    #    sql = sql.format(destination_table=destination_table, source_table=f"public.{source_table}")
    #    conn.execute(sa.text(sql))


def downgrade():
    pass
