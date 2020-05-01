"""Adds primary key id to user table.

Revision ID: 9a3478cbe76c
Revises: 6f04af3f261b
Create Date: 2020-04-29 12:21:04.458208

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import orm
from dispatch.auth.models import DispatchUser


# revision identifiers, used by Alembic.
revision = "9a3478cbe76c"
down_revision = "6f04af3f261b"
branch_labels = None
depends_on = None


def upgrade():
    # it's easier to drop the table and re-create instead of modifying
    conn = op.get_bind()
    session = orm.Session(bind=conn)
    results = conn.execute("select * from dispatch_user").fetchall()

    op.drop_table("dispatch_user")
    op.create_table(
        "dispatch_user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("password", sa.Binary(), nullable=False),
        sa.Column("role", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    for r in results:
        if len(r) == 5:
            session.add(DispatchUser(email=r[0], password=r[1], role=r[4]))
        else:
            session.add(DispatchUser(email=r[0], password=r[1]))
    session.commit()


def downgrade():
    pass
