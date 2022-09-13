import uuid
from datetime import datetime
from typing import Any, List, Optional

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB

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
    duplicate = Column(Boolean)
    supressed = Column(Boolean)
    raw = Column(JSONB)
    source = relationship("Source", backref="signals")
    source_id = Column(Integer, ForeignKey("source.id"))
    duplication_rule_id = Column(Integer, ForeignKey("duplication_rule.id"))
    suppression_rule_id = Column(Integer, ForeignKey("suppression_rule.id"))


# Pydantic models...
class SignalBase(DispatchBase):
    name: str
    raw: Any
    severity: Optional[Any]
    supressed: Optional[bool]
    duplicate: Optional[bool]
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
