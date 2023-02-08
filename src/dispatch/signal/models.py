import uuid
from datetime import datetime
from typing import Dict, List, Optional

from pydantic import Field
from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
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
from dispatch.database.core import Base
from dispatch.enums import DispatchEnum
from dispatch.models import DispatchBase, EvergreenMixin, PrimaryKey, ProjectMixin, TimeStampMixin
from dispatch.project.models import ProjectRead
from dispatch.tag.models import TagRead
from dispatch.tag_type.models import TagTypeRead


class FilterMode(DispatchEnum):
    active = "Active"
    monitor = "Monitor"
    inactive = "Inactive"


class SearchFilterMixin(Base, ProjectMixin, EvergreenMixin, TimeStampMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    name = Column(String)
    description = Column(String)
    expression = Column(JSON, nullable=False, default=[])
    creator_id = Column(Integer, ForeignKey(DispatchUser.id))
    creator = relationship("DispatchUser", backref="search_filters")
    mode = Column(String, default=FilterMode.active, nullable=False)
    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


class SuppressionFilter(Base, SearchFilterMixin):
    id = Column(Integer, primary_key=True)
    expiration = Column(DateTime, nullable=True)


class DuplicationFilter(Base, SearchFilterMixin):
    id = Column(Integer, primary_key=True)
    # number of seconds for duplication lookback default to 1 hour
    window = Column(Integer, default=(60 * 60))


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
    duplication_filter_id = Column(Integer, ForeignKey(DuplicationFilter.id))
    duplication_filter = relationship("DuplicationFilter", backref="signal")
    suppression_filter_id = Column(Integer, ForeignKey(SuppressionFilter.id))
    suppression_filter = relationship("SuppressionFilter", backref="signal")
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


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
    duplication_filter = relationship("DuplicationFilter", backref="signal_instances")
    duplication_filter_id = Column(Integer, ForeignKey(DuplicationFilter.id))
    fingerprint = Column(String)
    filter_action = Column(String)
    raw = Column(JSONB)
    signal = relationship("Signal", backref="instances")
    signal_id = Column(Integer, ForeignKey("signal.id"))
    suppression_filter = relationship("SuppressionFilter", backref="signal_instances")
    suppression_filter_id = Column(Integer, ForeignKey(SuppressionFilter.id))


# Pydantic models...
class SignalFilterBase(DispatchBase):
    mode: Optional[FilterMode] = FilterMode.active


class DuplicationFilterBase(SignalFilterBase):
    window: Optional[int] = 600
    expiration: Optional[datetime] = Field(None, nullable=True)


class DuplicationFilterCreate(DuplicationFilterBase):
    pass


class DuplicationFilterUpdate(DuplicationFilterBase):
    id: Optional[PrimaryKey]


class DuplicationFilterRead(DuplicationFilterBase):
    id: PrimaryKey


class SuppressionFilterBase(SignalFilterBase):
    expiration: Optional[datetime]
    tags: List[TagRead]


class SuppressionFilterCreate(SuppressionFilterBase):
    pass


class SuppressionFilterUpdate(SuppressionFilterBase):
    id: Optional[PrimaryKey]


class SuppressionFilterRead(SuppressionFilterBase):
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
    external_url: Optional[str]
    source: Optional[SourceBase]
    created_at: Optional[datetime] = None
    suppression_filters: Optional[List[SuppressionFilterRead]]
    duplication_filters: Optional[List[DuplicationFilterBase]]
    project: ProjectRead


class SignalCreate(SignalBase):
    suppression_filters: Optional[List[SuppressionFilterCreate]]
    duplication_filters: Optional[List[DuplicationFilterCreate]]


class SignalUpdate(SignalBase):
    id: PrimaryKey
    suppression_filters: Optional[List[SuppressionFilterUpdate]]
    duplication_filters: Optional[List[DuplicationFilterUpdate]]


class SignalRead(SignalBase):
    id: PrimaryKey
    suppression_filters: Optional[List[SuppressionFilterRead]]
    duplication_filters: Optional[List[DuplicationFilterRead]]


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
    raw: RawSignal
    suppression_filters: Optional[List[SuppressionFilterBase]]
    duplication_filters: Optional[List[DuplicationFilterBase]]
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
