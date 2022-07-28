from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Boolean, Integer, String
from sqlalchemy.event import listen
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.enums import Visibility
from dispatch.models import DispatchBase, ProjectMixin
from dispatch.models import NameStr, PrimaryKey
from dispatch.project.models import ProjectRead


class CaseType(ProjectMixin, Base):
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    slug = Column(String)
    name = Column(String)
    description = Column(String)
    visibility = Column(String, default=Visibility.open)
    default = Column(Boolean, default=False)
    enabled = Column(Boolean, default=True)
    exclude_from_metrics = Column(Boolean, default=False)

    # the catalog here is simple to help matching "named entities"
    search_vector = Column(TSVectorType("name", regconfig="pg_catalog.simple"))


listen(CaseType.default, "set", ensure_unique_default_per_project)


# Pydantic models
class CaseTypeBase(DispatchBase):
    default: Optional[bool] = False
    description: Optional[str] = Field(None, nullable=True)
    enabled: Optional[bool]
    exclude_from_metrics: Optional[bool] = False
    name: NameStr
    project: Optional[ProjectRead]
    visibility: Optional[str] = Field(None, nullable=True)


class CaseTypeCreate(CaseTypeBase):
    pass


class CaseTypeUpdate(CaseTypeBase):
    id: PrimaryKey = None


class CaseTypeRead(CaseTypeBase):
    id: PrimaryKey


class CaseTypePagination(DispatchBase):
    total: int
    items: List[CaseTypeRead] = []
