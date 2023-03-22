from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Integer, String
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, ProjectMixin
from dispatch.models import NameStr, PrimaryKey


class Workstream(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)

    # the catalog here is simple to help matching "named entities"
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))

    # relationships


# Pydantic models


class WorkstreamBase(DispatchBase):
    description: Optional[str] = Field(None, nullable=True)
    name: NameStr


class WorkstreamCreate(WorkstreamBase):
    pass


class WorkstreamUpdate(WorkstreamBase):
    id: PrimaryKey = None


class WorkstreamRead(WorkstreamBase):
    id: PrimaryKey


class WorkstreamPagination(DispatchBase):
    total: int
    items: List[WorkstreamRead] = []
