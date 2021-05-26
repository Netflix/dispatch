"""Ensures we always have a tag type

Revision ID: f011c050b9ba
Revises: 3e5f024e72f4
Create Date: 2021-06-01 10:33:32.006080

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

from sqlalchemy.orm import relationship, Session

from sqlalchemy.ext.declarative import declarative_base, declared_attr

Base = declarative_base()


# revision identifiers, used by Alembic.
revision = "f011c050b9ba"
down_revision = "3e5f024e72f4"
branch_labels = None
depends_on = None


class ProjectMixin(object):
    """Project mixin"""

    @declared_attr
    def project_id(cls):  # noqa
        return sa.Column(sa.Integer)


class TimeStampMixin(object):
    """Timestamping mixin"""

    created_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    created_at._creation_order = 9998
    updated_at = sa.Column(sa.DateTime, default=datetime.utcnow)
    updated_at._creation_order = 9998

    @staticmethod
    def _updated_at(mapper, connection, target):
        target.updated_at = datetime.utcnow()

    @classmethod
    def __declare_last__(cls):
        sa.event.listen(cls, "before_update", cls._updated_at)


class TagType(Base, TimeStampMixin, ProjectMixin):
    __tablename__ = "tag_type"
    id = sa.Column(sa.Integer, primary_key=True)
    name = sa.Column(sa.String)
    description = sa.Column(sa.String)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    default_tag_type = TagType(
        name="default", description="Default dispatch tag type.", project_id=1
    )
    session.add(default_tag_type)
    session.flush()

    op.execute("update tag set tag_type_id = 1 where tag_type_id is null;")
    op.alter_column("tag", "tag_type_id", existing_type=sa.INTEGER(), nullable=False)


def downgrade():
    op.alter_column("tag", "tag_type_id", existing_type=sa.INTEGER(), nullable=True)
