from typing import List, Optional
from pydantic import StrictBool, Field

from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, NameStr, TimeStampMixin, ProjectMixin, PrimaryKey
from dispatch.project.models import ProjectRead


class EntityType(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    field = Column(String)
    regular_expression = Column(String)
    global_find = Column(Boolean, default=False)
    enabled = Column(Boolean, default=False)
    search_vector = Column(
        TSVectorType(
            "name",
            "description",
            weights={"name": "A", "description": "B"},
            regconfig="pg_catalog.simple",
        )
    )


# Pydantic models
class EntityTypeBase(DispatchBase):
    name: Optional[NameStr]
    description: Optional[str] = Field(None, nullable=True)
    field: Optional[str] = Field(None, nullable=True, alias="jpath")
    global_find: Optional[StrictBool]
    enabled: Optional[bool]
    regular_expression: Optional[str] = Field(None, nullable=True)


class EntityTypeCreate(EntityTypeBase):
    project: ProjectRead


class EntityTypeUpdate(EntityTypeBase):
    id: PrimaryKey = None


class EntityTypeRead(EntityTypeBase):
    id: PrimaryKey
    project: ProjectRead


class EntityTypeReadMinimal(DispatchBase):
    id: PrimaryKey
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    global_find: Optional[StrictBool]
    enabled: Optional[bool]
    regular_expression: Optional[str] = Field(None, nullable=True)


class EntityTypePagination(DispatchBase):
    items: List[EntityTypeRead]
    total: int
