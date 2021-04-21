from datetime import datetime
from typing import List, Optional

from sqlalchemy import Boolean, Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin
from dispatch.project.models import ProjectRead
from dispatch.search.models import SearchFilterRead


# Association tables for many to many relationships
assoc_service_incidents = Table(
    "service_incident",
    Base.metadata,
    Column("incident_id", Integer, ForeignKey("incident.id")),
    Column("service_id", Integer, ForeignKey("service.id")),
    PrimaryKeyConstraint("incident_id", "service_id"),
)


assoc_service_filters = Table(
    "assoc_service_filters",
    Base.metadata,
    Column("service_id", Integer, ForeignKey("service.id", ondelete="CASCADE")),
    Column("search_filter_id", Integer, ForeignKey("search_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("service_id", "search_filter_id"),
)


# SQLAlchemy models...
class Service(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("external_id", "project_id"),)
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default=True)
    name = Column(String)
    type = Column(String, default="pagerduty-oncall")
    description = Column(String)
    external_id = Column(String)
    incidents = relationship("Incident", secondary=assoc_service_incidents, backref="services")

    # Relationships
    filters = relationship("SearchFilter", secondary=assoc_service_filters, backref="services")

    search_vector = Column(TSVectorType("name"))


# Pydantic models...
class ServiceBase(DispatchBase):
    name: Optional[str] = None
    external_id: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    type: Optional[str] = None


class ServiceCreate(ServiceBase):
    filters: Optional[List[SearchFilterRead]]
    project: ProjectRead


class ServiceUpdate(ServiceBase):
    filters: Optional[List[SearchFilterRead]]


class ServiceRead(ServiceBase):
    id: int
    filters: Optional[List[SearchFilterRead]]
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ServiceNested(ServiceBase):
    id: int


class ServicePagination(DispatchBase):
    total: int
    items: List[ServiceRead] = []
