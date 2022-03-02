from typing import Optional, List
from datetime import datetime
from pydantic import Field

from sqlalchemy import (
    JSON,
    Column,
    Integer,
    String,
    Boolean,
    Text,
    DateTime,
    Table,
    PrimaryKeyConstraint,
    ForeignKey,
    BigInteger,
)
from sqlalchemy.orm import relationship
from sqlalchemy import UniqueConstraint

from sqlalchemy_utils import TSVectorType
from dispatch.database.core import Base
from dispatch.models import DispatchBase, ProjectMixin, TimeStampMixin, PrimaryKey
from dispatch.project.models import ProjectRead
from dispatch.data.source.environment.models import SourceEnvironmentRead
from dispatch.data.source.data_format.models import SourceDataFormatRead
from dispatch.data.source.status.models import SourceStatusRead
from dispatch.data.source.transport.models import SourceTransportRead
from dispatch.data.source.type.models import SourceTypeRead
from dispatch.tag.models import TagRead
from dispatch.incident.models import IncidentRead

from dispatch.service.models import ServiceRead
from dispatch.data.alert.models import AlertRead

assoc_source_tags = Table(
    "assoc_source_tags",
    Base.metadata,
    Column("source_id", Integer, ForeignKey("source.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("source_id", "tag_id"),
)

assoc_source_incidents = Table(
    "assoc_source_incidents",
    Base.metadata,
    Column("source_id", Integer, ForeignKey("source.id", ondelete="CASCADE")),
    Column("incident_id", Integer, ForeignKey("incident.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("source_id", "incident_id"),
)


class Source(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    data_last_loaded_at = Column(DateTime)
    daily_volume = Column(Integer)
    aggregated = Column(Boolean)
    retention = Column(Integer)
    size = Column(BigInteger)
    cost = Column(Integer)
    delay = Column(Integer)
    environment = Column(String)
    external_id = Column(String)
    documentation = Column(Text)
    sampling_rate = Column(Integer)
    source_schema = Column(Text)
    links = Column(JSON)

    # relationships
    source_type = relationship("SourceType", uselist=False, backref="sources")
    source_type_id = Column(Integer, ForeignKey("source_type.id"))
    source_status = relationship("SourceStatus", uselist=False, backref="sources")
    source_status_id = Column(Integer, ForeignKey("source_status.id"))
    source_environment = relationship("SourceEnvironment", uselist=False, backref="sources")
    source_environment_id = Column(Integer, ForeignKey("source_environment.id"))
    source_data_format = relationship("SourceDataFormat", uselist=False, backref="sources")
    source_data_format_id = Column(Integer, ForeignKey("source_data_format.id"))
    source_transport_id = Column(Integer, ForeignKey("source_transport.id"))
    source_transport = relationship("SourceTransport", uselist=False, backref="sources")
    owner = relationship("Service", uselist=False, backref="sources")
    owner_id = Column(Integer, ForeignKey("service.id"))
    incidents = relationship("Incident", secondary=assoc_source_incidents, backref="sources")
    tags = relationship("Tag", secondary=assoc_source_tags, backref="sources")
    alerts = relationship("Alert", backref="source", cascade="all, delete-orphan")

    search_vector = Column(TSVectorType("name"))


class QueryReadNested(DispatchBase):
    id: PrimaryKey
    name: str
    description: str


# Pydantic models
class SourceBase(DispatchBase):
    name: Optional[str] = Field(None, nullable=False)
    description: Optional[str] = Field(None, nullable=True)
    data_last_loaded_at: Optional[datetime] = Field(None, nullable=True, title="Last Loaded")
    sampling_rate: Optional[int] = Field(
        None,
        nullable=True,
        title="Sampling Rate",
        lt=100,
        gt=1,
        description="Rate at which data is sampled (as a percentage) 100% meaning all data is captured.",
    )
    source_schema: Optional[str] = Field(None, nullable=True)
    documentation: Optional[str] = Field(None, nullable=True)
    retention: Optional[int] = Field(None, nullable=True)
    delay: Optional[int] = Field(None, nullable=True)
    size: Optional[int] = Field(None, nullable=True)
    external_id: Optional[str] = Field(None, nullable=True)
    aggregated: Optional[bool] = Field(False, nullable=True)
    links: Optional[List] = []
    tags: Optional[List[TagRead]] = []
    incidents: Optional[List[IncidentRead]] = []
    queries: Optional[List[QueryReadNested]] = []
    alerts: Optional[List[AlertRead]] = []
    cost: Optional[float]
    owner: Optional[ServiceRead] = Field(None, nullable=True)
    source_type: Optional[SourceTypeRead]
    source_environment: Optional[SourceEnvironmentRead]
    source_data_format: Optional[SourceDataFormatRead]
    source_status: Optional[SourceStatusRead]
    source_transport: Optional[SourceTransportRead]
    project: ProjectRead


class SourceCreate(SourceBase):
    pass


class SourceUpdate(SourceBase):
    id: Optional[PrimaryKey]


class SourceRead(SourceBase):
    id: PrimaryKey


class SourcePagination(DispatchBase):
    items: List[SourceRead]
    total: int
