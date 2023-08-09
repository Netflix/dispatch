from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy_utils import TSVectorType

from dispatch.enums import DispatchEnum
from dispatch.database.core import Base
from dispatch.models import (
    DispatchBase,
    NameStr,
    TimeStampMixin,
    ProjectMixin,
    PrimaryKey,
    Pagination,
)
from dispatch.project.models import ProjectRead


class EntityScopeEnum(DispatchEnum):
    single = "single"  # is only associated with a single definition
    multiple = "multiple"  # can be associated with multiple definitions
    all = "all"  # is associated with all definitions implicitly


class EntityType(Base, TimeStampMixin, ProjectMixin):
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    jpath = Column(String)
    regular_expression = Column(String)
    scope = Column(String, default=EntityScopeEnum.single, nullable=False)
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


class SignalRead(DispatchBase):
    id: PrimaryKey
    name: str
    owner: str
    conversation_target: Optional[str]
    description: Optional[str]
    variant: Optional[str]


class EntityTypeBase(DispatchBase):
    name: Optional[NameStr]
    description: Optional[str] = Field(None, nullable=True)
    jpath: Optional[str] = Field(None, nullable=True)
    scope: Optional[EntityScopeEnum] = Field(EntityScopeEnum.single, nullable=False)
    enabled: Optional[bool]
    signals: Optional[List[SignalRead]] = Field([], nullable=True)
    regular_expression: Optional[str] = Field(None, nullable=True)


class EntityTypeCreate(EntityTypeBase):
    id: Optional[PrimaryKey]
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
    scope: EntityScopeEnum
    enabled: Optional[bool]
    regular_expression: Optional[str] = Field(None, nullable=True)


class EntityTypePagination(Pagination):
    items: List[EntityTypeRead]
