from turtle import back
import uuid
from datetime import datetime
from typing import Any, List, Optional
from colorama import Fore

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table, PrimaryKeyConstraint, DateTime
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.enums import DispatchEnum
from dispatch.auth.models import DispatchUser

from dispatch.incident.models import CaseRead
from dispatch.models import DispatchBase, EvergreenMixin, PrimaryKey, TimeStampMixin, ProjectMixin

from dispatch.case.type.models import CaseTypeRead, CaseType
from dispatch.case.priority.models import CasePriority, CasePriorityRead
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
    Column("signal_instance_id", UUID, ForeignKey("signal_instance.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("signal_instance_id", "tag_id"),
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
    case_type_id = Column(Integer, ForeignKey(CaseType.id))
    case_type = relationship("CaseType", backref="signals")
    case_priority_id = Column(Integer, ForeignKey(CasePriority.id))
    case_priority = relationship("CasePriority", backref="signals")
    instances = relationship("SignalInstance", backref="Signal")
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


class SignalInstance(Base, TimeStampMixin, ProjectMixin):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship("Case", backref="signal_instances")
    signal_id = Column(Integer, ForeignKey("signal.id"))
    signal = relationship("Signal", backref="signal_instances")
    fingerprint = Column(String)
    severity = Column(String)
    raw = Column(JSONB)
    tags = relationship(
        "Tag",
        secondary=assoc_signal_instance_tags,
        backref="signal_instances",
    )


class SuppressionRule(Base, ProjectMixin, EvergreenMixin):
    id = Column(Integer, primary_key=True)
    creator_id = Column(Integer, ForeignKey(DispatchUser.id))
    creator = relationship("DispatchUser", backref="suppression_rule")
    signal_id = Column(Integer, ForeignKey(Signal.id))
    signal = relationship("Signal", backref="suppression_rule")
    mode = Column(String, default=RuleMode.active, nullable=False)
    expiration = Column(DateTime, nullable=True)

    # the tags to use for suppression
    tags = relationship("Tag", secondary=assoc_suppression_tags, backref="suppression_rules")


class DuplicationRule(Base, ProjectMixin, EvergreenMixin):
    id = Column(Integer, primary_key=True)
    signal_id = Column(Integer, ForeignKey(Signal.id))
    signal = relationship("Signal", backref="duplication_rules")
    mode = Column(String, default=RuleMode.active, nullable=False)

    # number of seconds for duplication lookback default to 1 hour
    window = Column(Integer, default=(60 * 60))

    # the tag types to use for deduplication
    tag_types = relationship(
        "TagType", secondary=assoc_duplication_tag_types, backref="duplication_rules"
    )


# Pydantic models...
class SignalRuleBase(DispatchBase):
    mode: Optional[RuleMode] = RuleMode.active


class DuplicationRuleBase(SignalRuleBase):
    window: Optional[int] = 60 * 60
    tag_types: List[TagTypeRead]


class SuppressionRuleBase(SignalRuleBase):
    expiration: Optional[datetime]
    tags: List[TagRead]


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
    supression_rule: Optional[SuppressionRuleBase]
    duplication_rule: Optional[DuplicationRuleBase]
    project: ProjectRead


class SignalCreate(SignalBase):
    pass


class SignalUpdate(SignalBase):
    id: PrimaryKey


class SignalRead(SignalBase):
    id: PrimaryKey


class SignalPagination(DispatchBase):
    items: List[SignalRead]
    total: int


class SignalInstanceBase(DispatchBase):
    raw: Any
    severity: Optional[Any]
    created_at: Optional[datetime] = None
    fingerprint: str
    project: ProjectRead
    case: Optional[CaseRead]
    tags: Optional[List[TagRead]]


class SignalInstanceCreate(SignalBase):
    pass


class SignalInstanceRead(SignalBase):
    id: uuid.UUID


class SignalInstancePagination(DispatchBase):
    items: List[SignalRead]
    total: int
