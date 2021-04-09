"""Adds column for FAIR form of loss category

Revision ID: b6da2dad0396
Revises: a769ea6bad64
Create Date: 2021-03-19 13:07:36.153462

"""
from alembic import op
import sqlalchemy as sa

from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql.expression import true

Base = declarative_base()


# revision identifiers, used by Alembic.
revision = "b6da2dad0396"
down_revision = "a769ea6bad64"
branch_labels = None
depends_on = None


class IncidentCostType(Base):
    __tablename__ = "incident_cost_type"
    # columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    category = Column(String)
    default = Column(Boolean, default=False)


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("incident_cost_type", sa.Column("category", sa.String(), nullable=True))

    # we set the category of the default response incident cost type
    bind = op.get_bind()
    session = Session(bind=bind)

    incident_cost_type = (
        session.query(IncidentCostType).filter(IncidentCostType.default == true()).one_or_none()
    )

    if incident_cost_type:
        incident_cost_type.category = "Primary"
        session.commit()
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("incident_cost_type", "category")
    # ### end Alembic commands ###
