import uuid
from typing import AnyStr, List

from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin, PrimaryKey

from dispatch.project.models import ProjectRead
from dispatch.data.source.models import SourceRead


class Signal(Base, TimeStampMixin, ProjectMixin):
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    severity = Column(String)
    detection = Column(String)
    fingerprint = Column(String)
    duplicate = Column(Boolean)
    supressed = Column(Boolean)
    raw = Column(JSONB)
    source = relationship("Source", backref="signals")
    source_id = Column(Integer, ForeignKey("source.id"))
    duplication_rule_id = Column(Integer, ForeignKey("duplication_rule.id"))
    supression_rule_id = Column(Integer, ForeignKey("supression_rule.id"))


# Pydantic models...
class SignalBase(DispatchBase):
    id: UUID
    raw: AnyStr
    severity: AnyStr
    supressed: bool
    duplicate: bool
    fingerprint: AnyStr
    detection: AnyStr
    source: SourceRead


class SignalCreate(SignalBase):
    project: ProjectRead


class SignalRead(SignalBase):
    id: PrimaryKey


class SignalPagination(DispatchBase):
    items: List[SignalRead]
    total: int
