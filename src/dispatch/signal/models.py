import uuid
from datetime import datetime
from typing import List, Optional, Any

from pydantic import Field
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    JSON,
    PrimaryKeyConstraint,
    String,
    Table,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.auth.models import DispatchUser
from dispatch.case.models import CaseReadMinimal
from dispatch.case.priority.models import CasePriority, CasePriorityRead
from dispatch.case.type.models import CaseType, CaseTypeRead
from dispatch.data.source.models import SourceBase
from dispatch.entity_type.models import EntityType
from dispatch.project.models import ProjectRead

from dispatch.database.core import Base
from dispatch.entity.models import EntityRead
from dispatch.entity_type.models import EntityTypeRead
from dispatch.tag.models import TagRead
from dispatch.enums import DispatchEnum
from dispatch.models import (
    DispatchBase,
    EvergreenMixin,
    NameStr,
    PrimaryKey,
    ProjectMixin,
    TimeStampMixin,
    Pagination,
)
from dispatch.workflow.models import WorkflowRead


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

assoc_signal_engagements = Table(
    "assoc_signal_engagements",
    Base.metadata,
    Column("signal_id", Integer, ForeignKey("signal.id", ondelete="CASCADE")),
    Column("signal_engagement_id", Integer, ForeignKey("signal_engagement.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("signal_id", "signal_engagement_id"),
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

assoc_signal_workflows = Table(
    "assoc_signal_workflows",
    Base.metadata,
    Column("signal_id", Integer, ForeignKey("signal.id", ondelete="CASCADE")),
    Column("workflow_id", Integer, ForeignKey("workflow.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("signal_id", "workflow_id"),
)


class SignalFilterMode(DispatchEnum):
    active = "active"
    monitor = "monitor"
    inactive = "inactive"
    expired = "expired"


class SignalFilterAction(DispatchEnum):
    deduplicate = "deduplicate"
    snooze = "snooze"
    none = "none"


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
    create_case = Column(Boolean, default=True)
    conversation_target = Column(String)
    default = Column(Boolean, default=False)

    oncall_service_id = Column(Integer, ForeignKey("service.id"))
    oncall_service = relationship("Service", foreign_keys=[oncall_service_id])
    engagements = relationship(
        "SignalEngagement", secondary=assoc_signal_engagements, backref="signals"
    )
    filters = relationship("SignalFilter", secondary=assoc_signal_filters, backref="signals")
    entity_types = relationship(
        "EntityType",
        secondary=assoc_signal_entity_types,
        backref="signals",
    )
    workflows = relationship(
        "Workflow",
        secondary=assoc_signal_workflows,
        backref="signals",
    )
    workflow_instances = relationship(
        "WorkflowInstance", backref="signal", cascade="all, delete-orphan"
    )

    tags = relationship(
        "Tag",
        secondary=assoc_signal_tags,
        backref="signals",
    )
    search_vector = Column(
        TSVectorType("name", "description", "variant", regconfig="pg_catalog.simple")
    )


class SignalEngagement(Base, ProjectMixin, TimeStampMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    message = Column(String, nullable=True)
    require_mfa = Column(Boolean, default=False)
    entity_type_id = Column(Integer, ForeignKey(EntityType.id))
    entity_type = relationship("EntityType", backref="signal_engagements")
    creator_id = Column(Integer, ForeignKey(DispatchUser.id))
    creator = relationship("DispatchUser", backref="signal_engagements")

    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
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
    engagement_thread_ts = Column(String, nullable=True)
    entities = relationship(
        "Entity",
        secondary=assoc_signal_instance_entities,
        backref="signal_instances",
    )
    case_type_id = Column(Integer, ForeignKey(CaseType.id))
    case_type = relationship("CaseType", backref="signal_instances")
    case_priority_id = Column(Integer, ForeignKey(CasePriority.id))
    case_priority = relationship("CasePriority", backref="signal_instances")
    filter_action = Column(String)
    canary = Column(Boolean, default=False)
    raw = Column(JSONB)
    signal = relationship("Signal", backref="instances")
    signal_id = Column(Integer, ForeignKey("signal.id"))


# Pydantic models
class Service(DispatchBase):
    id: PrimaryKey
    description: Optional[str] = Field(None, nullable=True)
    external_id: str
    is_active: Optional[bool] = None
    name: NameStr
    type: Optional[str] = Field(None, nullable=True)


class SignalEngagementBase(DispatchBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    require_mfa: Optional[bool] = False
    entity_type: Optional[EntityTypeRead] = None
    message: Optional[str] = Field(None, nullable=True)


class SignalFilterBase(DispatchBase):
    mode: Optional[SignalFilterMode] = SignalFilterMode.active
    expression: Optional[List[dict]] = Field([], nullable=True)
    name: NameStr
    action: SignalFilterAction = SignalFilterAction.snooze
    description: Optional[str] = Field(None, nullable=True)
    window: Optional[int] = 600
    expiration: Optional[datetime] = Field(None, nullable=True)


class SignalFilterUpdate(SignalFilterBase):
    id: PrimaryKey


class SignalEngagementCreate(SignalEngagementBase):
    project: ProjectRead


class SignalEngagementRead(SignalEngagementBase):
    id: PrimaryKey


class SignalEngagementPagination(Pagination):
    items: List[SignalEngagementRead]


class SignalFilterCreate(SignalFilterBase):
    project: ProjectRead


class SignalFilterRead(SignalFilterBase):
    id: PrimaryKey


class SignalFilterPagination(Pagination):
    items: List[SignalFilterRead]


class SignalBase(DispatchBase):
    case_priority: Optional[CasePriorityRead]
    case_type: Optional[CaseTypeRead]
    conversation_target: Optional[str]
    create_case: Optional[bool] = True
    created_at: Optional[datetime] = None
    default: Optional[bool] = False
    description: Optional[str]
    enabled: Optional[bool] = False
    external_id: str
    external_url: Optional[str]
    name: str
    oncall_service: Optional[Service]
    owner: str
    project: ProjectRead
    source: Optional[SourceBase]
    variant: Optional[str]


class SignalCreate(SignalBase):
    filters: Optional[List[SignalFilterRead]] = []
    engagements: Optional[List[SignalEngagementRead]] = []
    entity_types: Optional[List[EntityTypeRead]] = []
    workflows: Optional[List[WorkflowRead]] = []
    tags: Optional[List[TagRead]] = []


class SignalUpdate(SignalBase):
    id: PrimaryKey
    engagements: Optional[List[SignalEngagementRead]] = []
    filters: Optional[List[SignalFilterRead]] = []
    entity_types: Optional[List[EntityTypeRead]] = []
    workflows: Optional[List[WorkflowRead]] = []
    tags: Optional[List[TagRead]] = []


class SignalRead(SignalBase):
    id: PrimaryKey
    engagements: Optional[List[SignalEngagementRead]] = []
    entity_types: Optional[List[EntityTypeRead]] = []
    filters: Optional[List[SignalFilterRead]] = []
    workflows: Optional[List[WorkflowRead]] = []
    tags: Optional[List[TagRead]] = []


class SignalReadMinimal(DispatchBase):
    id: PrimaryKey
    name: str
    owner: str
    conversation_target: Optional[str]
    description: Optional[str]
    variant: Optional[str]
    external_id: str
    enabled: Optional[bool] = False
    external_url: Optional[str]
    create_case: Optional[bool] = True
    created_at: Optional[datetime] = None


class SignalPagination(Pagination):
    items: List[SignalRead]


class AdditionalMetadata(DispatchBase):
    name: Optional[str]
    value: Optional[Any]
    type: Optional[str]
    important: Optional[bool]


class SignalInstanceBase(DispatchBase):
    project: Optional[ProjectRead]
    case: Optional[CaseReadMinimal]
    canary: Optional[bool] = False
    entities: Optional[List[EntityRead]] = []
    raw: dict[str, Any]
    external_id: Optional[str]
    filter_action: SignalFilterAction = None
    created_at: Optional[datetime] = None


class SignalInstanceCreate(SignalInstanceBase):
    signal: Optional[SignalRead]
    case_priority: Optional[CasePriorityRead]
    case_type: Optional[CaseTypeRead]


class SignalInstanceRead(SignalInstanceBase):
    id: uuid.UUID
    signal: SignalRead


class SignalInstancePagination(Pagination):
    items: List[SignalInstanceRead]
