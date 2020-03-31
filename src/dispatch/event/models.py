from enum import Enum

from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    PrimaryKeyConstraint,
    String,
    Table,
    event,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin
from dispatch.plugins.base import plugins


EventSource = Enum(
    "EventSource", [[plugin.slug.replace("-", "_"), plugin.title] for plugin in plugins.all()]
)

assoc_event_tags = Table(
    "assoc_event_tags",
    Base.metadata,
    Column("event_id", Integer, ForeignKey("event.id")),
    Column("tag_id", Integer, ForeignKey("tag.id")),
    PrimaryKeyConstraint("event_id", "tag_id"),
)


# SQLAlchemy Model
class Event(Base, TimeStampMixin):
    # columns
    id = Column(Integer, primary_key=True)
    uuid = Column(UUID(as_uuid=True), unique=True, nullable=False)
    started_at = Column(DateTime)
    ended_at = Column(DateTime)
    source = Column(String, nullable=False)
    description = Column(String, nullable=False)

    # relationships
    individual_id = Column(Integer, ForeignKey("individual.id"))
    incident_id = Column(Integer, ForeignKey("incident.id"))
    tags = relationship("Tag", secondary=assoc_event_tags, backref="events")

    # full text search capabilities
    search_vector = Column(
        TSVectorType("source", "description", weights={"source": "A", "description": "B"})
    )

    @staticmethod
    def _ended_at(mapper, connection, target):
        if not target.ended_at:
            target.ended_at = target.started_at

    @classmethod
    def __declare_last__(cls):
        event.listen(cls, "before_update", cls._ended_at)


# Pydantic Models
class EventBase(DispatchBase):
    started_at: DateTime
    ended_at: DateTime
    source: EventSource
    description: str


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventRead(EventBase):
    pass


class EventNested(EventBase):
    id: int
