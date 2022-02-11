from typing import Optional, List
from datetime import datetime
from pydantic import Field

from sqlalchemy import (
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

from sqlalchemy_utils import TSVectorType

from dispatch.enums import DispatchEnum
from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, PrimaryKey


class SourceTypes(DispatchEnum):
    iceberg = "Iceberg"
    elasticsearch = "Elasticsearch"
    s3 = "S3"
    hive = "Hive"


class Statuses(DispatchEnum):
    deprecated = "Deprecated"
    alpha = "Alpha"
    beta = "Beta"
    stable = "Stable"


class Transports(DispatchEnum):
    rest = "REST"
    syslog = "Syslog"


class DataFormats(DispatchEnum):
    json = "JSON"
    csv = "CSV"


class Environments(DispatchEnum):
    test = "Test"
    prod = "Prod"


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


class Source(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    last_refreshed = Column(DateTime)
    daily_volume = Column(Integer)
    aggregated = Column(Boolean)
    retention = Column(Integer)
    size = Column(BigInteger)
    delay = Column(Integer)
    environment = Column(String)
    external_id = Column(String)
    documentation = Column(Text)
    sampling_rate = Column(Integer)
    source_schema = Column(Text)
    source_type = Column(String)
    data_format = Column(String)
    status = Column(String)
    transport = Column(String)
    owner = relationship("Service", uselist=False, backref="source")
    owner_id = Column(Integer, ForeignKey("service.id"))
    incidents = relationship("Incident", secondary=assoc_source_incidents, backref="sources")
    tags = relationship("Tag", secondary=assoc_source_tags, backref="sources")
    alerts = relationship("Alert", backref="source", cascade="all, delete-orphan")
    search_vector = Column(TSVectorType("name"))


# Pydantic models
class SourceBase(DispatchBase):
    name: Optional[str] = Field(None, nullable=False)
    description: Optional[str] = Field(None, nullable=True)
    last_refreshed: Optional[datetime] = Field(None, nullable=True, title="Last Refreshed")
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
    environment: Optional[Environments] = Field(Environments.prod, nullable=False)
    external_id: Optional[str] = Field(None, nullable=True)
    source_type: Optional[SourceTypes] = Field(SourceTypes.iceberg, nullable=False)
    data_format: Optional[DataFormats] = Field(DataFormats.json, nullable=False)
    status: Optional[Statuses] = Field(Statuses.alpha, nullable=False)
    transport: Optional[Transports] = Field(Transports.rest, nullable=False)
    aggregated: Optional[bool] = Field(False, nullable=True)


class SourceCreate(SourceBase):
    pass


class SourceUpdate(SourceBase):
    id: Optional[PrimaryKey]


class SourceRead(SourceBase):
    id: PrimaryKey


class SourcePagination(DispatchBase):
    items: List[SourceRead]
    total: int
