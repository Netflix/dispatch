from datetime import datetime
from typing import List, Optional
from pydantic import Field
from dispatch.models import EvergreenBase, EvergreenMixin, PrimaryKey

from sqlalchemy import Boolean, Column, ForeignKey, Integer, PrimaryKeyConstraint, String, Table
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin
from dispatch.project.models import ProjectRead
from dispatch.search_filter.models import SearchFilterRead


assoc_service_filters = Table(
    "assoc_service_filters",
    Base.metadata,
    Column("service_id", Integer, ForeignKey("service.id", ondelete="CASCADE")),
    Column("search_filter_id", Integer, ForeignKey("search_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("service_id", "search_filter_id"),
)


# SQLAlchemy models...
class Service(Base, TimeStampMixin, ProjectMixin, EvergreenMixin):
    __table_args__ = (UniqueConstraint("external_id", "project_id"),)
    id = Column(Integer, primary_key=True)
    is_active = Column(Boolean, default=True)
    name = Column(String)
    type = Column(String, default="pagerduty-oncall")
    description = Column(String)
    external_id = Column(String)

    # Relationships
    filters = relationship("SearchFilter", secondary=assoc_service_filters, backref="services")

    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


# Pydantic models...
class ServiceBase(EvergreenBase):
    name: Optional[str] = Field(None, nullable=True)
    external_id: Optional[str] = Field(None, nullable=True)
    description: Optional[str] = Field(None, nullable=True)
    is_active: Optional[bool] = None
    type: Optional[str] = Field(None, nullable=True)


class ServiceCreate(ServiceBase):
    filters: Optional[List[SearchFilterRead]] = []
    project: ProjectRead


class ServiceUpdate(ServiceBase):
    filters: Optional[List[SearchFilterRead]] = []


class ServiceRead(ServiceBase):
    id: PrimaryKey
    filters: Optional[List[SearchFilterRead]] = []
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ServiceNested(ServiceBase):
    id: PrimaryKey


class ServicePagination(DispatchBase):
    total: int
    items: List[ServiceRead] = []
