from typing import Optional, List

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin
from dispatch.project.models import ProjectRead
from dispatch.tag_type.models import TagTypeRead, TagTypeCreate, TagTypeUpdate


class Tag(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)

    # Columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    uri = Column(String)
    source = Column(String)
    discoverable = Column(Boolean, default=True)

    # Relationships
    tag_type_id = Column(Integer, ForeignKey("tag_type.id"), nullable=False)
    tag_type = relationship("TagType", backref="tag")

    search_vector = Column(TSVectorType("name"))


# Pydantic models
class TagBase(DispatchBase):
    name: Optional[str]
    source: Optional[str]
    uri: Optional[str]
    discoverable: Optional[bool] = True
    description: Optional[str]


class TagCreate(TagBase):
    id: Optional[int]
    tag_type: TagTypeCreate
    project: ProjectRead


class TagUpdate(TagBase):
    id: Optional[int]
    tag_type: Optional[TagTypeUpdate]


class TagRead(TagBase):
    id: int
    tag_type: Optional[TagTypeRead]
    project: ProjectRead


class TagPagination(DispatchBase):
    items: List[TagRead]
    total: int
