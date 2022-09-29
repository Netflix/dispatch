from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, NameStr, TimeStampMixin, ProjectMixin, PrimaryKey
from dispatch.project.models import ProjectRead


class TagType(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    exclusive = Column(Boolean, default=False)
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


# Pydantic models
class TagTypeBase(DispatchBase):
    name: NameStr
    exclusive: Optional[bool] = False
    description: Optional[str] = Field(None, nullable=True)


class TagTypeCreate(TagTypeBase):
    project: ProjectRead


class TagTypeUpdate(TagTypeBase):
    id: PrimaryKey = None


class TagTypeRead(TagTypeBase):
    id: PrimaryKey
    project: ProjectRead


class TagTypePagination(DispatchBase):
    items: List[TagTypeRead]
    total: int
