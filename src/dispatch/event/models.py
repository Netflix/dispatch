from datetime import datetime
from uuid import UUID

from typing import Optional
from dispatch.models import PrimaryKey

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID as SQLAlchemyUUID
from sqlalchemy_utils import TSVectorType, JSONType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin


# SQLAlchemy Model
class Event(Base, TimeStampMixin):
    # columns
    id = Column(Integer, primary_key=True)
    uuid = Column(SQLAlchemyUUID(as_uuid=True), unique=True, nullable=False)
    started_at = Column(DateTime, nullable=False)
    ended_at = Column(DateTime, nullable=False)
    source = Column(String, nullable=False)
    description = Column(String, nullable=False)
    details = Column(JSONType, nullable=True)

    # relationships
    individual_id = Column(Integer, ForeignKey("individual_contact.id", ondelete="CASCADE"))
    incident_id = Column(Integer, ForeignKey("incident.id", ondelete="CASCADE"))

    dispatch_user_id = Column(
        Integer, ForeignKey("dispatch_core.dispatch_user.id", ondelete="CASCADE")
    )
    case_id = Column(Integer, ForeignKey("case.id", ondelete="CASCADE"))

    # full text search capabilities
    search_vector = Column(
        TSVectorType("source", "description", weights={"source": "A", "description": "B"})
    )


# Pydantic Models
class EventBase(DispatchBase):
    uuid: UUID
    started_at: datetime
    ended_at: datetime
    source: str
    description: str
    details: Optional[dict]


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventRead(EventBase):
    pass
