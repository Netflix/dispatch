from typing import Optional, List
from pydantic import Field

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, TimeStampMixin, ProjectMixin, PrimaryKey
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

    # the catalog here is simple to help matching "named entities"
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


# Pydantic models
class TagBase(DispatchBase):
    name: Optional[str] = Field(None, nullable=True)
    source: Optional[str] = Field(None, nullable=True)
    uri: Optional[str] = Field(None, nullable=True)
    discoverable: Optional[bool] = True
    description: Optional[str] = Field(None, nullable=True)


class TagCreate(TagBase):
    id: Optional[PrimaryKey]
    tag_type: TagTypeCreate
    project: ProjectRead


class TagUpdate(TagBase):
    id: Optional[PrimaryKey]
    tag_type: Optional[TagTypeUpdate]


class TagRead(TagBase):
    id: PrimaryKey
    tag_type: Optional[TagTypeRead]
    project: ProjectRead


class TagPagination(DispatchBase):
    items: List[TagRead]
    total: int
