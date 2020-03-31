from enum import Enum

from typing import Optional

from sqlalchemy import Column, Integer, String, ForeignKey, PrimaryKeyConstraint, Table
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
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    description = Column(String, nullable=False)
    author = Column(String)

    # relationships
    incident_id = Column(Integer, ForeignKey("incident.id"))
    tags = relationship("Tag", secondary=assoc_event_tags, backref="events")

    search_vector = Column(
        TSVectorType(
            "source",
            "description",
            "author",
            weights={"source": "A", "description": "B", "author": "C"},
        )
    )


# Pydantic Models
class EventBase(DispatchBase):
    source: EventSource
    description: str
    author: Optional[str]


class EventCreate(EventBase):
    pass


class EventUpdate(EventBase):
    pass


class EventRead(EventBase):
    pass


class EventNested(EventBase):
    id: int
