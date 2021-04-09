from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Table
from sqlalchemy.orm import backref, relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.incident_priority.models import (
    IncidentPriorityCreate,
    IncidentPriorityRead,
    IncidentPriorityUpdate,
)
from dispatch.incident_type.models import IncidentTypeCreate, IncidentTypeRead, IncidentTypeUpdate
from dispatch.models import DispatchBase, TermReadNested, TimeStampMixin, ProjectMixin
from dispatch.project.models import ProjectRead
from dispatch.term.models import TermCreate

# Association tables for many to many relationships
assoc_service_incident_priorities = Table(
    "service_incident_priority",
    Base.metadata,
    Column("incident_priority_id", Integer, ForeignKey("incident_priority.id")),
    Column("service_id", Integer, ForeignKey("service.id")),
    PrimaryKeyConstraint("incident_priority_id", "service_id"),
)

assoc_service_incident_types = Table(
    "service_incident_type",
    Base.metadata,
    Column("incident_type_id", Integer, ForeignKey("incident_type.id")),
    Column("service_id", Integer, ForeignKey("service.id")),
    PrimaryKeyConstraint("incident_type_id", "service_id"),
)

assoc_service_incidents = Table(
    "service_incident",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id")),
    Column("service_id", Integer, ForeignKey("service.id")),
    PrimaryKeyConstraint("incident_id", "service_id"),
)

assoc_service_terms = Table(
    "service_terms",
    Base.metadata,
    Column("term_id", Integer, ForeignKey("term.id")),
    Column("service_id", Integer, ForeignKey("service.id")),
    PrimaryKeyConstraint("term_id", "service_id"),
)


# SQLAlchemy models...
class Service(Base, TimeStampMixin, ProjectMixin):
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default=True)
    name = Column(String)
    type = Column(String, default="pagerduty-oncall")
    description = Column(String)
    external_id = Column(String)
    incidents = relationship("Incident", secondary=assoc_service_incidents, backref="services")
    incident_priorities = relationship(
        "IncidentPriority", secondary=assoc_service_incident_priorities, backref="services"
    )
    incident_types = relationship(
        "IncidentType", secondary=assoc_service_incident_types, backref="services"
    )
    terms = relationship(
        "Term", secondary=assoc_service_terms, backref=backref("services", cascade="all")
    )

    search_vector = Column(TSVectorType("name"))


# Pydantic models...
class ServiceBase(DispatchBase):
    name: Optional[str] = None
    external_id: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    type: Optional[str] = None


class ServiceCreate(ServiceBase):
    terms: Optional[List[TermCreate]] = []
    incident_priorities: Optional[List[IncidentPriorityCreate]] = []
    incident_types: Optional[List[IncidentTypeCreate]] = []
    project: ProjectRead


class ServiceUpdate(ServiceBase):
    terms: Optional[List[TermCreate]] = []
    incident_priorities: Optional[List[IncidentPriorityUpdate]] = []
    incident_types: Optional[List[IncidentTypeUpdate]] = []


class ServiceRead(ServiceBase):
    id: int
    incident_priorities: Optional[List[IncidentPriorityRead]] = []
    incident_types: Optional[List[IncidentTypeRead]] = []
    terms: Optional[List[TermReadNested]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ServiceNested(ServiceBase):
    id: int


class ServicePagination(DispatchBase):
    total: int
    items: List[ServiceRead] = []
