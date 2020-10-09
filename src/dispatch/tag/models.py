from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy_utils import TSVectorType

from dispatch.database import Base
from dispatch.models import DispatchBase, TimeStampMixin
from dispatch.tag_type.models import TagTypeCreate, TagTypeRead, TagTypeUpdate


class Tag(Base, TimeStampMixin):
    # Columns
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True)
    description = Column(String)
    uri = Column(String)
    source = Column(String)
    discoverable = Column(Boolean, default=True)

    # Relationships
    tag_type_id = Column(Integer, ForeignKey("tag_type.id"))
    tag_type = relationship("TagType", backref="tag")

    search_vector = Column(TSVectorType("name"))


# Pydantic models
class TagBase(DispatchBase):
    name: str
    source: Optional[str]
    uri: Optional[str]
    discoverable: Optional[bool] = True
    description: Optional[str]


class TagCreate(TagBase):
    tag_type: TagTypeCreate


class TagUpdate(TagBase):
    id: int
    tag_type: TagTypeUpdate


class TagRead(TagBase):
    id: int
    tag_type: TagTypeRead


class TagPagination(DispatchBase):
    items: List[TagRead]
    total: int
