import uuid
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin

from dispatch.project.models import ProjectRead
from dispatch.data.source.models import SourceBase


class Signal(Base, TimeStampMixin, ProjectMixin):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    external_url = Column(String)
    external_id = Column(String)
    severity = Column(String)
    detection = Column(String)
    detection_variant = Column(String)
    raw = Column(JSONB)
    source = relationship("Source", backref="signals")
    source_id = Column(Integer, ForeignKey("source.id"))
    case_id = Column(Integer, ForeignKey("case.id"))
    duplication_rule_id = Column(Integer, ForeignKey("duplication_rule.id"))
    suppression_rule_id = Column(Integer, ForeignKey("suppression_rule.id"))

    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


# Pydantic models...
class SignalBase(DispatchBase):
    name: str
    raw: Any
    severity: Optional[Any]
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
