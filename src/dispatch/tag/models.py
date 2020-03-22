from typing import Optional, List

from sqlalchemy import Column, Integer, String

from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase, tags_incidents, TimeStampMixin


class Tag(Base, TimeStampMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    uri = Column(String)
    source = Column(String)
    type = Column(String)
    incidents = relationship("Incident", secondary=tags_incidents, backref="tags")
    search_vector = Column(TSVectorType("name"))


# Pydantic models
class TagBase(DispatchBase):
    name: str
    source: str
    type: str
    uri: Optional[str]
    description: Optional[str]


class TagCreate(TagBase):
    pass


class TagUpdate(TagBase):
    id: int


class TagRead(TagBase):
    id: int


class TagPagination(DispatchBase):
    items: List[TagRead]
    total: int
