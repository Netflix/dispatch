from pydantic import Field

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import (
    DispatchBase,
    ProjectMixin,
    PrimaryKey,
    Pagination,
)
from dispatch.definition.models import DefinitionRead
from dispatch.project.models import ProjectRead


# SQLAlchemy models...
class Term(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("text", "project_id"),)
    id = Column(Integer, primary_key=True)
    text = Column(String)
    discoverable = Column(Boolean, default=True)
    search_vector = Column(
        TSVectorType(
            "text",
            regconfig="pg_catalog.simple",
        )
    )


# Pydantic models...
class TermBase(DispatchBase):
    id: PrimaryKey | None = None
    text: str | None = Field(None, nullable=True)
    discoverable: bool | None = True


class TermCreate(TermBase):
    definitions: list[DefinitionRead | None] = []
    project: ProjectRead


class TermUpdate(TermBase):
    definitions: list[DefinitionRead | None] = []


class TermRead(TermBase):
    id: PrimaryKey
    definitions: list[DefinitionRead | None] = []


class TermPagination(Pagination):
    items: list[TermRead] = []
