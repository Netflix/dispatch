from enum import Enum

from typing import Optional

from sqlalchemy import Column, Integer, String
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin
from dispatch.plugins.base import plugins


TimelineSource = Enum(
    "TimelineSource", [[plugin.slug.replace("-", "_"), plugin.title] for plugin in plugins.all()]
)


# SQLAlchemy Model
class Timeline(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    source = Column(String, nullable=False)
    description = Column(String, nullable=False)
    author = Column(String)

    search_vector = Column(
        TSVectorType(
            "source",
            "description",
            "author",
            weights={"source": "A", "description": "B", "author": "C"},
        )
    )


# Pydantic Models
class TimelineBase(DispatchBase):
    source: TimelineSource
    description: str
    author: Optional[str]


class TimelineCreate(TimelineBase):
    pass


class TimelineUpdate(TimelineBase):
    pass


class TimelineRead(TimelineBase):
    pass


class TimelineNested(TimelineBase):
    id: int
