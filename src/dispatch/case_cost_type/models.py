from datetime import datetime
from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.event import listen

from sqlalchemy_utils import TSVectorType, JSONType

from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.models import (
    DispatchBase,
    NameStr,
    ProjectMixin,
    TimeStampMixin,
    Pagination,
    PrimaryKey,
)
from dispatch.project.models import ProjectRead


# SQLAlchemy Model
class CaseCostType(Base, TimeStampMixin, ProjectMixin):
    # columns
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    category = Column(String)
    details = Column(JSONType, nullable=True)
    default = Column(Boolean, default=False)
    editable = Column(Boolean, default=True)

    # full text search capabilities
    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


listen(CaseCostType.default, "set", ensure_unique_default_per_project)


# Pydantic Models
class CaseCostTypeBase(DispatchBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    category: Optional[str] = Field(None, nullable=True)
    details: Optional[dict] = {}
    created_at: Optional[datetime]
    default: Optional[bool]
    editable: Optional[bool]


class CaseCostTypeCreate(CaseCostTypeBase):
    project: ProjectRead


class CaseCostTypeUpdate(CaseCostTypeBase):
    id: PrimaryKey = None


class CaseCostTypeRead(CaseCostTypeBase):
    id: PrimaryKey


class CaseCostTypePagination(Pagination):
    items: List[CaseCostTypeRead] = []
