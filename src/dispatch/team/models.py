from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.incident_priority.models import IncidentPriorityCreate, IncidentPriorityRead
from dispatch.incident_type.models import IncidentTypeCreate, IncidentTypeRead
from dispatch.term.models import TermCreate
from dispatch.models import ContactBase, ContactMixin, DispatchBase, TermReadNested

assoc_team_contact_incident_priorities = Table(
    "team_contact_incident_priority",
    Base.metadata,
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id")),
    Column("team_contact_id", Integer, ForeignKey("team_contact.id")),
    PrimaryKeyConstraint("incident_priority_id", "team_contact_id"),
)

assoc_team_contact_incident_types = Table(
    "team_contact_incident_type",
    Base.metadata,
    Column("incident_type_id", Integer, ForeignKey("incident_type.id")),
    Column("team_contact_id", Integer, ForeignKey("team_contact.id")),
    PrimaryKeyConstraint("incident_type_id", "team_contact_id"),
)

assoc_team_contact_incidents = Table(
    "team_contact_incident",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id")),
    Column("team_contact_id", Integer, ForeignKey("team_contact.id")),
    PrimaryKeyConstraint("incident_id", "team_contact_id"),
)

assoc_team_contact_terms = Table(
    "team_contact_terms",
    Base.metadata,
    Column("term_id", Integer, ForeignKey("term.id")),
    Column("team_contact_id", ForeignKey("team_contact.id")),
    PrimaryKeyConstraint("term_id", "team_contact_id"),
)


class TeamContact(Base, ContactMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    notes = Column(String)
    incident_priorities = relationship(
        "IncidentPriority", secondary=assoc_team_contact_incident_priorities, backref="teams"
    )
    incident_types = relationship(
        "IncidentType", secondary=assoc_team_contact_incident_types, backref="teams"
    )
    incidents = relationship(
        "Incident", secondary=assoc_team_contact_incidents, backref="teams"
    )  # I'm not sure this needs to be set explicitly rather than via a query
    terms = relationship("Term", secondary=assoc_team_contact_terms, backref="teams")
    search_vector = Column(TSVectorType("name", "notes", weights={"name": "A", "notes": "B"}))


class TeamContactBase(ContactBase):
    name: str
    notes: Optional[str]


class TeamContactCreate(TeamContactBase):
    terms: Optional[List[TermCreate]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []
    incident_types: Optional[List[IncidentTypeCreate]] = []


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
