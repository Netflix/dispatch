"""Adds incident role mappings

Revision ID: b73416df5744
Revises: 9fcf205ba6a5
Create Date: 2021-08-09 15:29:24.856985

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Boolean, Column, Integer, String, PrimaryKeyConstraint, Table, ForeignKey
from sqlalchemy.orm import relationship, Session
from collections import defaultdict


# revision identifiers, used by Alembic.
revision = "b73416df5744"
down_revision = "9fcf205ba6a5"
branch_labels = None
depends_on = None

Base = declarative_base()


class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)


class Service(Base):
    __tablename__ = "service"
    id = Column(Integer, primary_key=True)


class IncidentType(Base):
    __tablename__ = "incident_type"
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project")
    commander_service_id = Column(Integer, ForeignKey("service.id"))
    commander_service = relationship("Service", foreign_keys=[commander_service_id])

    liaison_service_id = Column(Integer, ForeignKey("service.id"))
    liaison_service = relationship("Service", foreign_keys=[liaison_service_id])


class IncidentPriority(Base):
    __tablename__ = "incident_priority"
    id = Column(Integer, primary_key=True)


assoc_incident_roles_incident_types = Table(
    "incident_role_incident_type",
    Base.metadata,
    Column("incident_role_id", Integer, ForeignKey("incident_role.id")),
    Column("incident_type_id", Integer, ForeignKey("incident_type.id")),
    PrimaryKeyConstraint("incident_role_id", "incident_type_id"),
)

assoc_incident_roles_incident_priorities = Table(
    "incident_role_incident_priorities",
    Base.metadata,
    Column("incident_role_id", Integer, ForeignKey("incident_role.id")),
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id")),
    PrimaryKeyConstraint("incident_role_id", "incident_priority_id"),
)


class IncidentRole(Base):
    __tablename__ = "incident_role"
    # Columns
    id = Column(Integer, primary_key=True)
    role = Column(String)

    enabled = Column(Boolean, default=True)
    order = Column(Integer)

    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project")

    # Relationships
    incident_types = relationship("IncidentType", secondary=assoc_incident_roles_incident_types)
    incident_priorities = relationship(
        "IncidentPriority", secondary=assoc_incident_roles_incident_priorities
    )

    service_id = Column(Integer, ForeignKey("service.id"))
    service = relationship("Service")


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "incident_role",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(), nullable=True),
        sa.Column("enabled", sa.Boolean(), nullable=True),
        sa.Column("order", sa.Integer(), nullable=True),
        sa.Column("service_id", sa.Integer(), nullable=True),
        sa.Column("individual_id", sa.Integer(), nullable=True),
        sa.Column("project_id", sa.Integer(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["individual_id"],
            ["individual_contact.id"],
        ),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["service_id"],
            ["service.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "incident_role_incident_priority",
        sa.Column("incident_role_id", sa.Integer(), nullable=False),
        sa.Column("incident_priority_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["incident_priority_id"],
            ["incident_priority.id"],
        ),
        sa.ForeignKeyConstraint(
            ["incident_role_id"],
            ["incident_role.id"],
        ),
        sa.PrimaryKeyConstraint("incident_role_id", "incident_priority_id"),
    )
    op.create_table(
        "incident_role_tag",
        sa.Column("incident_role_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["incident_role_id"],
            ["incident_role.id"],
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["tag.id"],
        ),
        sa.PrimaryKeyConstraint("incident_role_id", "tag_id"),
    )
    op.create_table(
        "incident_role_incident_type",
        sa.Column("incident_role_id", sa.Integer(), nullable=False),
        sa.Column("incident_type_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["incident_role_id"],
            ["incident_role.id"],
        ),
        sa.ForeignKeyConstraint(
            ["incident_type_id"],
            ["incident_type.id"],
        ),
        sa.PrimaryKeyConstraint("incident_role_id", "incident_type_id"),
    )

    # migrate old incident type mappings to incident roles
    bind = op.get_bind()
    session = Session(bind=bind)

    roles = defaultdict(list)

    for i_type in session.query(IncidentType).all():
        # group by types
        if i_type.commander_service_id:
            roles[(i_type.project_id, i_type.commander_service_id, "Incident Commander")].append(
                i_type
            )

        if i_type.liaison_service_id:
            roles[(i_type.project_id, i_type.liaison_service_id, "Liaison")].append(i_type)

    incident_priorities = session.query(IncidentPriority).all()

    for k, v in roles.items():
        project_id, service_id, role = k
        session.add(
            IncidentRole(
                project_id=project_id,
                incident_types=v,
                incident_priorities=incident_priorities,
                role=role,
                service_id=service_id,
            )
        )

    session.commit()

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("incident_role_incident_type")
    op.drop_table("incident_role_tag")
    op.drop_table("incident_role_incident_priority")
    op.drop_table("incident_role")
    # ### end Alembic commands ###
