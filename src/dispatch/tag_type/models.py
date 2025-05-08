from pydantic import Field

from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.sql.sqltypes import Boolean
from sqlalchemy_utils import TSVectorType

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


class TagType(Base, TimeStampMixin, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    exclusive = Column(Boolean, default=False)
    required = Column(Boolean, default=False)
    discoverable_case = Column(Boolean, default=True)
    discoverable_incident = Column(Boolean, default=True)
    discoverable_query = Column(Boolean, default=True)
    discoverable_signal = Column(Boolean, default=True)
    discoverable_source = Column(Boolean, default=True)
    discoverable_document = Column(Boolean, default=True)
    color = Column(String)
    icon = Column(String)
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))
    use_for_project_folder = Column(Boolean, default=False, server_default="f")


# Pydantic models
class TagTypeBase(DispatchBase):
    name: NameStr
    exclusive: bool | None = False
    required: bool | None = False
    discoverable_case: bool | None = True
    discoverable_incident: bool | None = True
    discoverable_query: bool | None = True
    discoverable_signal: bool | None = True
    discoverable_source: bool | None = True
    discoverable_document: bool | None = True
    description: str | None = Field(None, nullable=True)
    color: str | None = Field(None, nullable=True)
    icon: str | None = Field(None, nullable=True)
    use_for_project_folder: bool | None = False


class TagTypeCreate(TagTypeBase):
    project: ProjectRead


class TagTypeUpdate(TagTypeBase):
    id: PrimaryKey | None = None


class TagTypeRead(TagTypeBase):
    id: PrimaryKey
    project: ProjectRead


class TagTypePagination(Pagination):
    items: list[TagTypeRead]
