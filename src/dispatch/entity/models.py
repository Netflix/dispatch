from typing import List, Optional
from pydantic import StrictBool, Field

from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, NameStr, TimeStampMixin, ProjectMixin, PrimaryKey
from dispatch.project.models import ProjectRead


class Entity(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    regular_expression = Column(String)
    global_find = Column(Boolean, default=False)
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


# Pydantic models
class EntityBase(DispatchBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    global_find: Optional[StrictBool]
    regular_expression: Optional[str] = Field(None, nullable=True)


class EntityCreate(EntityBase):
    project: ProjectRead


class EntityUpdate(EntityBase):
    id: PrimaryKey = None


class EntityRead(EntityBase):
    id: PrimaryKey
    global_find: Optional[StrictBool]
    project: ProjectRead


class EntityReadMinimal(DispatchBase):
    id: PrimaryKey
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    global_find: Optional[StrictBool]
    regular_expression: Optional[str] = Field(None, nullable=True)


class EntityPagination(DispatchBase):
    items: List[EntityRead]
    total: int
