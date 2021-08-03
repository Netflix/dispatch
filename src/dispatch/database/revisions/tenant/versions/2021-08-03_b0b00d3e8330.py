"""Migrates workflow instance enums

Revision ID: b0b00d3e8330
Revises: 2780d28e4f39
Create Date: 2021-08-03 10:01:48.442379

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "b0b00d3e8330"
down_revision = "2780d28e4f39"
branch_labels = None
depends_on = None


def upgrade():
    # generate existing slugs
    conn = op.get_bind()
    res = conn.execute("select id, status from workflow_instance")
    results = res.fetchall()

    for r in results:
        conn.execute(
            f"update workflow_instance set status = '{r[1].capitalize()}' where id = {r[0]}"
        )


def downgrade():
    conn = op.get_bind()
    res = conn.execute("select id, status from workflow_instance")
    results = res.fetchall()

    for r in results:
        conn.execute(f"update workflow_instance set status = '{r[1].lower()}' where id = {r[0]}")
