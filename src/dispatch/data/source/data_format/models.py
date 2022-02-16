from typing import Optional, List
from pydantic import Field

from sqlalchemy import (
    Column,
    Integer,
    String,
)
from sqlalchemy import UniqueConstraint

from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base
from dispatch.models import DispatchBase, ProjectMixin, PrimaryKey
from dispatch.project.models import ProjectRead


class SourceDataFormat(Base, ProjectMixin):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    search_vector = Column(TSVectorType("name"))


class SourceDataFormatBase(DispatchBase):
    name: Optional[str] = Field(None, nullable=False)
    description: Optional[str] = Field(None, nullable=True)


class SourceDataFormatRead(SourceDataFormatBase):
    id: PrimaryKey
    project: ProjectRead


class SourceDataFormatCreate(SourceDataFormatBase):
    project: ProjectRead


class SourceDataFormatUpdate(SourceDataFormatBase):
    id: PrimaryKey


class SourceDataFormatPagination(DispatchBase):
    items: List[SourceDataFormatRead]
    total: int
