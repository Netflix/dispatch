from pydantic import Field

from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy import UniqueConstraint

from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, ProjectMixin, Pagination, PrimaryKey
from dispatch.project.models import ProjectRead


class SourceType(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


class SourceTypeBase(DispatchBase):
    name: str | None = Field(None, nullable=False)
    description: str | None = None


class SourceTypeRead(SourceTypeBase):
    id: PrimaryKey
    project: ProjectRead


class SourceTypeCreate(SourceTypeBase):
    project: ProjectRead


class SourceTypeUpdate(SourceTypeBase):
    id: PrimaryKey


class SourceTypePagination(Pagination):
    items: list[SourceTypeRead]
