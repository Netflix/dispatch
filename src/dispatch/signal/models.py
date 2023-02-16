import uuid
from datetime import datetime
from typing import List, Optional, Dict
from pydantic import Field

from sqlalchemy.orm import relationship
from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    Table,
    PrimaryKeyConstraint,
    DateTime,
    Boolean,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.enums import DispatchEnum

from dispatch.models import DispatchBase, EvergreenMixin, PrimaryKey, TimeStampMixin, ProjectMixin

from dispatch.case.models import CaseRead
from dispatch.case.type.models import CaseTypeRead, CaseType
from dispatch.case.priority.models import CasePriority, CasePriorityRead
from dispatch.entity.models import EntityRead
from dispatch.entity_type.models import EntityTypeRead, EntityTypeCreate
from dispatch.tag.models import TagRead
from dispatch.project.models import ProjectRead
from dispatch.data.source.models import SourceBase
from dispatch.tag_type.models import TagTypeRead


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

assoc_duplication_tag_types = Table(
    "assoc_duplication_rule_tag_types",
    Base.metadata,
    Column("duplication_rule_id", Integer, ForeignKey("duplication_rule.id", ondelete="CASCADE")),
    Column("tag_type_id", Integer, ForeignKey("tag_type.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("duplication_rule_id", "tag_type_id"),
)

assoc_suppression_tags = Table(
    "assoc_suppression_rule_tags",
    Base.metadata,
    Column("suppression_rule_id", Integer, ForeignKey("suppression_rule.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("suppression_rule_id", "tag_id"),
)


class SuppressionRule(Base, ProjectMixin, EvergreenMixin):
    id = Column(Integer, primary_key=True)
    mode = Column(String, default=RuleMode.active, nullable=False)
    expiration = Column(DateTime, nullable=True)

    # the tags to use for suppression
    tags = relationship("Tag", secondary=assoc_suppression_tags, backref="suppression_rules")


class DuplicationRule(Base, ProjectMixin, EvergreenMixin):
    id = Column(Integer, primary_key=True)
    mode = Column(String, default=RuleMode.active, nullable=False)

    # number of seconds for duplication lookback default to 1 hour
    window = Column(Integer, default=(60 * 60))

    # the tag types to use for deduplication
    tag_types = relationship(
        "TagType", secondary=assoc_duplication_tag_types, backref="duplication_rules"
    )


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
    case_type_id = Column(Integer, ForeignKey(CaseType.id))
    case_type = relationship("CaseType", backref="signals")
    case_priority_id = Column(Integer, ForeignKey(CasePriority.id))
    case_priority = relationship("CasePriority", backref="signals")
    duplication_rule_id = Column(Integer, ForeignKey(DuplicationRule.id))
    duplication_rule = relationship("DuplicationRule", backref="signal")
    entity_types = relationship(
        "EntityType",
        secondary=assoc_signal_entity_types,
        backref="signals",
    )
    suppression_rule_id = Column(Integer, ForeignKey(SuppressionRule.id))
    suppression_rule = relationship("SuppressionRule", backref="signal")
    tags = relationship(
        "Tag",
        secondary=assoc_signal_tags,
        backref="signals",
    )
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


class SignalInstance(Base, TimeStampMixin, ProjectMixin):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case = relationship("Case", backref="signal_instances")
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))
    duplication_rule = relationship("DuplicationRule", backref="signal_instances")
    duplication_rule_id = Column(Integer, ForeignKey(DuplicationRule.id))
    entities = relationship(
        "Entity",
        secondary=assoc_signal_instance_entities,
        backref="signal_instances",
    )
    fingerprint = Column(String)
    raw = Column(JSONB)
    signal = relationship("Signal", backref="instances")
    signal_id = Column(Integer, ForeignKey("signal.id"))
    suppression_rule = relationship("SuppressionRule", backref="signal_instances")
    suppression_rule_id = Column(Integer, ForeignKey(SuppressionRule.id))
    tags = relationship(
        "Tag",
        secondary=assoc_signal_instance_tags,
        backref="signal_instances",
    )


# Pydantic models...
class SignalRuleBase(DispatchBase):
    mode: Optional[RuleMode] = RuleMode.active


class DuplicationRuleBase(SignalRuleBase):
    window: Optional[int] = 600
    tag_types: List[TagTypeRead]


class DuplicationRuleCreate(DuplicationRuleBase):
    pass


class DuplicationRuleUpdate(DuplicationRuleBase):
    id: Optional[PrimaryKey]


class DuplicationRuleRead(DuplicationRuleBase):
    id: PrimaryKey


class SuppressionRuleBase(SignalRuleBase):
    expiration: Optional[datetime]
    tags: List[TagRead]


class SuppressionRuleCreate(SuppressionRuleBase):
    pass


class SuppressionRuleUpdate(SuppressionRuleBase):
    id: Optional[PrimaryKey]


class SuppressionRuleRead(SuppressionRuleBase):
    id: PrimaryKey


class SignalBase(DispatchBase):
    name: str
    owner: str
    description: Optional[str]
    variant: Optional[str]
    case_type: Optional[CaseTypeRead]
    case_priority: Optional[CasePriorityRead]
    external_id: str
    external_url: Optional[str]
    source: Optional[SourceBase]
    created_at: Optional[datetime] = None
    entity_types: Optional[List[EntityTypeRead]]
    suppression_rule: Optional[SuppressionRuleRead]
    duplication_rule: Optional[DuplicationRuleBase]
    project: ProjectRead


class SignalCreate(SignalBase):
    entity_types: Optional[EntityTypeCreate]
    suppression_rule: Optional[SuppressionRuleCreate]
    duplication_rule: Optional[DuplicationRuleCreate]


class SignalUpdate(SignalBase):
    id: PrimaryKey
    entity_types: Optional[List[EntityTypeRead]] = []
    suppression_rule: Optional[SuppressionRuleUpdate]
    duplication_rule: Optional[DuplicationRuleUpdate]


class SignalRead(SignalBase):
    id: PrimaryKey
    entity_types: Optional[List[EntityTypeRead]]
    suppression_rule: Optional[SuppressionRuleRead]
    duplication_rule: Optional[DuplicationRuleRead]


class SignalPagination(DispatchBase):
    items: List[SignalRead]
    total: int


class AdditionalMetadata(DispatchBase):
    name: Optional[str]
    value: Optional[str]
    type: Optional[str]
    important: Optional[bool]


class RawSignal(DispatchBase):
    action: Optional[List[Dict]] = []
    additional_metadata: Optional[List[AdditionalMetadata]] = Field([], alias="additionalMetadata")
    asset: Optional[List[Dict]] = []
    identity: Optional[Dict] = {}
    origin_location: Optional[List[Dict]] = Field([], alias="originLocation")
    variant: Optional[str] = None
    created_at: Optional[datetime] = Field(None, fields="createdAt")
    id: Optional[str]


class SignalInstanceBase(DispatchBase):
    project: ProjectRead
    case: Optional[CaseRead]
    entities: Optional[List[EntityRead]] = []
    tags: Optional[List[TagRead]] = []
    raw: RawSignal
    suppression_rule: Optional[SuppressionRuleBase]
    duplication_rule: Optional[DuplicationRuleBase]
    created_at: Optional[datetime] = None


class SignalInstanceCreate(SignalInstanceBase):
    pass


class SignalInstanceRead(SignalInstanceBase):
    id: uuid.UUID
    fingerprint: str = None
    signal: SignalRead


class SignalInstancePagination(DispatchBase):
    items: List[SignalInstanceRead]
    total: int
