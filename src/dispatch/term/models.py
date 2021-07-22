from typing import List, Optional
from dispatch.models import PrimaryKey

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DefinitionNested, DefinitionReadNested, DispatchBase, ProjectMixin
from dispatch.project.models import ProjectRead


# SQLAlchemy models...
class Term(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("text", "project_id"),)
    id = Column(Integer, primary_key=True)
    text = Column(String)
    discoverable = Column(Boolean, default=True)
    search_vector = Column(TSVectorType("text"))


# Pydantic models...
class TermBase(DispatchBase):
    id: Optional[int] = None
    text: Optional[str] = None
    discoverable: Optional[bool] = True


class TermCreate(TermBase):
    definitions: Optional[List[DefinitionNested]] = []
    project: ProjectRead


class TermUpdate(TermBase):
    definitions: Optional[List[DefinitionNested]] = []


class TermRead(TermBase):
    id: PrimaryKey
    definitions: Optional[List[DefinitionReadNested]] = []


class TermPagination(DispatchBase):
    total: int
    items: List[TermRead] = []
