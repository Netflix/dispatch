from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.incident_priority.models import IncidentPriorityCreate, IncidentPriorityRead
from dispatch.incident_type.models import IncidentTypeCreate, IncidentTypeRead
from dispatch.project.models import ProjectRead
from dispatch.term.models import TermCreate
from dispatch.models import ContactBase, ContactMixin, DispatchBase, TermReadNested, ProjectMixin

assoc_team_contact_incidents = Table(
    "team_contact_incident",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id")),
    Column("team_contact_id", Integer, ForeignKey("team_contact.id")),
    PrimaryKeyConstraint("incident_id", "team_contact_id"),
)

assoc_team_filters = Table(
    "assoc_team_contact_filters",
    Base.metadata,
    Column("team_contact_id", Integer, ForeignKey("team_contact.id", ondelete="CASCADE")),
    Column("search_filter_id", Integer, ForeignKey("search_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("team_contact_id", "search_filter_id"),
)


class TeamContact(Base, ContactMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("email", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    notes = Column(String)
    incidents = relationship(
        "Incident", secondary=assoc_team_contact_incidents, backref="teams"
    )  # I'm not sure this needs to be set explicitly rather than via a query

    filters = relationship("SearchFilter", secondary=assoc_team_filters, backref="teams")
    search_vector = Column(TSVectorType("name", "notes", weights={"name": "A", "notes": "B"}))


class TeamContactBase(ContactBase):
    name: str
    notes: Optional[str]


class TeamContactCreate(TeamContactBase):
    terms: Optional[List[TermCreate]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []
    incident_types: Optional[List[IncidentTypeCreate]] = []
    project: ProjectRead


class TeamContactUpdate(TeamContactBase):
    terms: Optional[List[TermCreate]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []
    incident_types: Optional[List[IncidentTypeCreate]] = []


class TeamContactRead(TeamContactBase):
    id: int
    incident_priorities: Optional[List[IncidentPriorityRead]] = []
    incident_types: Optional[List[IncidentTypeRead]] = []
    terms: Optional[List[TermReadNested]] = []
    created_at: datetime
    updated_at: datetime


class TeamPagination(DispatchBase):
    total: int
    items: List[TeamContactRead] = []
