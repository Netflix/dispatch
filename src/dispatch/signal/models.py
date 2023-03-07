import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

from pydantic import Field
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.auth.models import DispatchUser
from dispatch.case.models import CaseRead
from dispatch.case.priority.models import CasePriority, CasePriorityRead
from dispatch.case.type.models import CaseType, CaseTypeRead
from dispatch.data.source.models import SourceBase
from dispatch.project.models import ProjectRead

from dispatch.database.core import Base
from dispatch.entity.models import EntityRead
from dispatch.entity_type.models import EntityTypeCreate, EntityTypeRead
from dispatch.tag.models import TagRead
from dispatch.enums import DispatchEnum
from dispatch.models import (
    DispatchBase,
    EvergreenMixin,
    NameStr,
    PrimaryKey,
    ProjectMixin,
    TimeStampMixin,
)


class RuleMode(DispatchEnum):
    active = "Active"
    monitor = "Monitor"
    inactive = "Inactive"


assoc_signal_instance_tags = Table(
    "assoc_signal_instance_tags",
    Base.metadata,
    Column(
        "signal_instance_id",
        UUID(as_uuid=True),
        ForeignKey("signal_instance.id", ondelete="CASCADE"),
    ),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("signal_instance_id", "tag_id"),
)


assoc_signal_tags = Table(
    "assoc_signal_tags",
    Base.metadata,
    Column("signal_id", Integer, ForeignKey("signal.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("signal_id", "tag_id"),
)

assoc_signal_filters = Table(
    "assoc_signal_filters",
    Base.metadata,
    Column("signal_id", Integer, ForeignKey("signal.id", ondelete="CASCADE")),
    Column("signal_filter_id", Integer, ForeignKey("signal_filter.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("signal_id", "signal_filter_id"),
)

assoc_signal_instance_entities = Table(
    "assoc_signal_instance_entities",
    Base.metadata,
    Column(
        "signal_instance_id",
        UUID(as_uuid=True),
        ForeignKey("signal_instance.id", ondelete="CASCADE"),
    ),
    Column("entity_id", Integer, ForeignKey("entity.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("signal_instance_id", "entity_id"),
)

assoc_signal_entity_types = Table(
    "assoc_signal_entity_types",
    Base.metadata,
    Column("signal_id", Integer, ForeignKey("signal.id", ondelete="CASCADE")),
    Column("entity_type_id", Integer, ForeignKey("entity_type.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("signal_id", "entity_type_id"),
)


class SignalFilterMode(DispatchEnum):
    active = "active"
    monitor = "monitor"
    inactive = "inactive"
    expired = "expired"


class SignalFilterAction(DispatchEnum):
    deduplicate = "deduplicate"
    snooze = "snooze"


class Signal(Base, TimeStampMixin, ProjectMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    owner = Column(String)
    description = Column(String)
    external_url = Column(String)
    external_id = Column(String)
    source = relationship("Source", backref="signals")
    source_id = Column(Integer, ForeignKey("source.id"))
    variant = Column(String)
    loopin_signal_identity = Column(Boolean, default=False)
    enabled = Column(Boolean, default=False)
    case_type_id = Column(Integer, ForeignKey(CaseType.id))
    case_type = relationship("CaseType", backref="signals")
    case_priority_id = Column(Integer, ForeignKey(CasePriority.id))
    case_priority = relationship("CasePriority", backref="signals")
    filters = relationship("SignalFilter", secondary=assoc_signal_filters, backref="signals")
    entity_types = relationship(
        "EntityType",
        secondary=assoc_signal_entity_types,
        backref="signals",
    )
    tags = relationship(
        "Tag",
        secondary=assoc_signal_tags,
        backref="signals",
    )
    search_vector = Column(
        TSVectorType("name", "description", "variant", regconfig="pg_catalog.simple")
    )


class SignalFilter(Base, ProjectMixin, EvergreenMixin, TimeStampMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    expression = Column(JSON, nullable=False, default=[])
    mode = Column(String, default=SignalFilterMode.active, nullable=False)
    action = Column(String, nullable=False)
    expiration = Column(DateTime, nullable=True)
    window = Column(
        Integer, default=(60 * 60)
    )  # number of seconds for duplication lookback default to 1 hour

    creator_id = Column(Integer, ForeignKey(DispatchUser.id))
    creator = relationship("DispatchUser", backref="signal_filters")

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


class SignalInstance(Base, TimeStampMixin, ProjectMixin):
    id = Column(UUID(as_uuid=True), primary_key=True, default=lambda: str(uuid.uuid4()))
    case = relationship("Case", backref="signal_instances")
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))
    entities = relationship(
        "Entity",
        secondary=assoc_signal_instance_entities,
        backref="signal_instances",
    )
    fingerprint = Column(String)
    filter_action = Column(String)
    raw = Column(JSONB)
    signal = relationship("Signal", backref="instances")
    signal_id = Column(Integer, ForeignKey("signal.id"))


# Pydantic models...
class SignalFilterBase(DispatchBase):
    mode: Optional[SignalFilterMode] = SignalFilterMode.active
    expression: List[dict]
    name: NameStr
    action: SignalFilterAction = SignalFilterAction.snooze
    description: Optional[str] = Field(None, nullable=True)
    window: Optional[int] = 600
    expiration: Optional[datetime] = Field(None, nullable=True)


class SignalFilterUpdate(SignalFilterBase):
    id: PrimaryKey


class SignalFilterCreate(SignalFilterBase):
    project: ProjectRead


class SignalFilterRead(SignalFilterBase):
    id: PrimaryKey


class SignalFilterPagination(DispatchBase):
    items: List[SignalFilterRead]
    total: int


class SignalBase(DispatchBase):
    name: str
    owner: str
    description: Optional[str]
    variant: Optional[str]
    case_type: Optional[CaseTypeRead]
    case_priority: Optional[CasePriorityRead]
    external_id: str
    enabled: Optional[bool] = False
    external_url: Optional[str]
    source: Optional[SourceBase]
    created_at: Optional[datetime] = None
    filters: Optional[List[SignalFilterRead]] = []
    entity_types: Optional[List[EntityTypeRead]] = []
    tags: Optional[List[TagRead]] = []
    project: ProjectRead


class SignalCreate(SignalBase):
    entity_types: Optional[EntityTypeCreate] = []


class SignalUpdate(SignalBase):
    id: PrimaryKey
    entity_types: Optional[List[EntityTypeRead]] = []


class SignalRead(SignalBase):
    id: PrimaryKey
    entity_types: Optional[List[EntityTypeRead]] = []


class SignalPagination(DispatchBase):
    items: List[SignalRead]
    total: int


class AdditionalMetadata(DispatchBase):
    name: Optional[str]
    value: Optional[Any]
    type: Optional[str]
    important: Optional[bool]


class SignalInstanceBase(DispatchBase):
    project: ProjectRead
    case: Optional[CaseRead]
    entities: Optional[List[EntityRead]] = []
    raw: dict[str, Any]
    filter_action: SignalFilterAction = None
    created_at: Optional[datetime] = None


class SignalInstanceCreate(SignalInstanceBase):
    pass


class SignalInstanceRead(SignalInstanceBase):
    id: uuid.UUID
    fingerprint: Optional[str]
    signal: SignalRead


class SignalInstancePagination(DispatchBase):
    items: List[SignalInstanceRead]
    total: int
