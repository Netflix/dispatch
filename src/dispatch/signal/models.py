import uuid
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Table, PrimaryKeyConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.incident.models import CaseRead
from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin

from dispatch.case.type.models import CaseTypeRead, CaseType
from dispatch.tag.models import TagRead
from dispatch.project.models import ProjectRead
from dispatch.data.source.models import SourceBase

assoc_signal_instance_tags = Table(
    "assoc_signal_instance_tags",
    Base.metadata,
    Column("signal_instance_id", UUID, ForeignKey("signal_instance.id", ondelete="CASCADE")),
    Column("tag_id", Integer, ForeignKey("tag.id", ondelete="CASCADE")),
    PrimaryKeyConstraint("signal_instance_id", "tag_id"),
)


class Signal(Base, TimeStampMixin, ProjectMixin):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    owner = Column(String)
    description = Column(String)
    external_url = Column(String)
    external_id = Column(String)
    source = relationship("Source", backref="signals")
    source_id = Column(Integer, ForeignKey("source.id"))
    variant = Column(String)
    case_type_id = Column(Integer, ForeignKey(CaseType.id))
    case_type = relationship("CaseType", backref="signal")
    instances = relationship("SignalInstances", backref="Signal")
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


class SignalInstance(Base, TimeStampMixin, ProjectMixin):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(Integer, ForeignKey("case.id"))
    case = relationship("Case", backref="signal_instances")
    fingerprint = Column(String)
    severity = Column(String)
    raw = Column(JSONB)
    tags = relationship(
        "Tag",
        secondary=assoc_signal_instance_tags,
        backref="signal_instances",
    )


# Pydantic models...
class SignalBase(DispatchBase):
    name: str
    owner: str
    description: str
    variant: str
    case_type: Optional[CaseTypeRead]
    external_id: Optional[str]
    external_url: Optional[str]
    source: Optional[SourceBase]
    created_at: Optional[datetime] = None
    project: ProjectRead


class SignalCreate(SignalBase):
    pass


class SignalRead(SignalBase):
    id: uuid.UUID


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
