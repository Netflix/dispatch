from datetime import datetime
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
    description: str | None = Field(None, nullable=True)
    category: str | None = Field(None, nullable=True)
    details: dict | None = {}
    created_at: datetime | None
    editable: bool | None
    model_type: str | None = Field(None, nullable=False)


class CaseCostTypeCreate(CaseCostTypeBase):
    project: ProjectRead


class CaseCostTypeUpdate(CaseCostTypeBase):
    id: PrimaryKey = None


class CaseCostTypeRead(CaseCostTypeBase):
    id: PrimaryKey


class CaseCostTypePagination(Pagination):
    items: list[CaseCostTypeRead] = []
