from datetime import datetime
from pydantic import Field, AnyHttpUrl

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
from dispatch.models import (
    DispatchBase,
    ProjectMixin,
    Pagination,
    TimeStampMixin,
    PrimaryKey,
)
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

    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


class QueryReadMinimal(DispatchBase):
    id: PrimaryKey
    name: str
    description: str


class Link(DispatchBase):
    id: int | None
    name: str | None
    description: str | None
    href: AnyHttpUrl | None


# Pydantic models
class SourceBase(DispatchBase):
    name: str | None = Field(None, nullable=False)
    description: str | None = Field(None, nullable=True)
    data_last_loaded_at: datetime | None = Field(None, nullable=True, title="Last Loaded")
    sampling_rate: int | None = Field(
        None,
        nullable=True,
        title="Sampling Rate",
        lt=101,
        gt=1,
        description="Rate at which data is sampled (as a percentage) 100% meaning all data is captured.",
    )
    source_schema: str | None = Field(None, nullable=True)
    documentation: str | None = Field(None, nullable=True)
    retention: int | None = Field(None, nullable=True)
    delay: int | None = Field(None, nullable=True)
    size: int | None = Field(None, nullable=True)
    external_id: str | None = Field(None, nullable=True)
    aggregated: bool | None = Field(False, nullable=True)
    links: list[Link | None] = Field(default_factory=list)
    tags: list[TagRead | None] = []
    incidents: list[IncidentRead | None] = []
    queries: list[QueryReadMinimal | None] = []
    alerts: list[AlertRead | None] = []
    cost: float | None
    owner: ServiceRead | None = Field(None, nullable=True)
    source_type: SourceTypeRead | None
    source_environment: SourceEnvironmentRead | None
    source_data_format: SourceDataFormatRead | None
    source_status: SourceStatusRead | None
    source_transport: SourceTransportRead | None
    project: ProjectRead


class SourceCreate(SourceBase):
    pass


class SourceUpdate(SourceBase):
    id: PrimaryKey | None


class SourceRead(SourceBase):
    id: PrimaryKey


class SourcePagination(Pagination):
    items: list[SourceRead]
