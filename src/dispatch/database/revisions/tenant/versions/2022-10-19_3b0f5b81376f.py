"""Creates and sets a default incident severity to all incidents in all projects

Revision ID: 3b0f5b81376f
Revises: d6438d754467
Create Date: 2022-10-19 13:13:17.581202

"""
from alembic import op

from pydantic import BaseModel
from pydantic.color import Color
from pydantic.types import constr, conint

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql.expression import true
from sqlalchemy.sql.schema import UniqueConstraint

from dispatch.incident.severity import service as incident_severity_service

PrimaryKey = conint(gt=0, lt=2147483647)
NameStr = constr(regex=r"^(?!\s*$).+", strip_whitespace=True, min_length=3)

Base = declarative_base()

# revision identifiers, used by Alembic.
revision = "3b0f5b81376f"
down_revision = "d6438d754467"
branch_labels = None
depends_on = None


class Project(Base):
    __tablename__ = "project"
    id = Column(Integer, primary_key=True)
    name = Column(String)


class IncidentSeverity(Base):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    __tablename__ = "incident_severity"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    color = Column(String)
    enabled = Column(Boolean, default=True)
    default = Column(Boolean, default=False)

    # This column is used to control how severities should be displayed
    # Lower numbers will be shown first.
    view_order = Column(Integer, default=9999)

    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"))
    project = relationship("Project")


class Incident(Base):
    __tablename__ = "incident"
    id = Column(Integer, primary_key=True)

    incident_severity = relationship("IncidentSeverity", backref="incident")
    incident_severity_id = Column(Integer, ForeignKey("incident_severity.id"))

    project = relationship("Project")
    project_id = Column(Integer, ForeignKey("project.id", ondelete="CASCADE"))


class DispatchBase(BaseModel):
    class Config:
        orm_mode = True
        validate_assignment = True
        arbitrary_types_allowed = True
        anystr_strip_whitespace = True


class ProjectRead(DispatchBase):
    id: PrimaryKey
    name: NameStr


class IncidentSeverityCreate(DispatchBase):
    color: Color
    default: bool
    description: str
    enabled: bool
    name: NameStr
    project: ProjectRead
    view_order: int


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    projects = session.query(Project).all()
    for project in projects:
        print(f"Creating default incident severity in project {project.name}...")
        incident_severity_in = IncidentSeverityCreate(
            name="Undetermined",
            description="The severity of the incident has not yet been determined.",
            color="#9e9e9e",
            enabled=True,
            default=True,
            project=project,
            view_order=1,
        )
        incident_severity = incident_severity_service.create(
            db_session=session, incident_severity_in=incident_severity_in
        )
        print(f"Default incident severity created in project {project.name}.")

        print(f"Setting default incident severity to all incidents in project {project.name}...")
        incident_severity = (
            session.query(IncidentSeverity)
            .filter(IncidentSeverity.project_id == project.id)
            .filter(IncidentSeverity.default == true())
            .first()
        )
        incidents = session.query(Incident).filter(Incident.project_id == project.id).all()
        for incident in incidents:
            incident.incident_severity = incident_severity
            session.add(incident)
            session.commit()
        print(f"Default incident severity set to all incidents in project {project.name}.")


def downgrade():
    pass
