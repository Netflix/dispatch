from datetime import datetime
from typing import List, Optional
from pydantic import Field

from sqlalchemy import Column, Integer, String, Boolean

from sqlalchemy_utils import TSVectorType, JSONType

from dispatch.database.core import Base
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
    editable = Column(Boolean, default=True)
    model_type = Column(String, nullable=True)

    # full text search capabilities
    search_vector = Column(
        TSVectorType("name", "description", weights={"name": "A", "description": "B"})
    )


# Pydantic Models
class CaseCostTypeBase(DispatchBase):
    name: NameStr
    description: Optional[str] = Field(None, nullable=True)
    category: Optional[str] = Field(None, nullable=True)
    details: Optional[dict] = {}
    created_at: Optional[datetime]
    editable: Optional[bool]
    model_type: Optional[str] = Field(None, nullable=False)


class CaseCostTypeCreate(CaseCostTypeBase):
    project: ProjectRead


class CaseCostTypeUpdate(CaseCostTypeBase):
    id: PrimaryKey = None


class CaseCostTypeRead(CaseCostTypeBase):
    id: PrimaryKey


class CaseCostTypePagination(Pagination):
    items: List[CaseCostTypeRead] = []
