from datetime import datetime
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
class IncidentCostType(Base, TimeStampMixin, ProjectMixin):
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


listen(IncidentCostType.default, "set", ensure_unique_default_per_project)


# Pydantic Models
class IncidentCostTypeBase(DispatchBase):
    name: NameStr
    description: str | None = Field(None, nullable=True)
    category: str | None = Field(None, nullable=True)
    details: dict | None = {}
    created_at: datetime | None
    default: bool | None
    editable: bool | None


class IncidentCostTypeCreate(IncidentCostTypeBase):
    project: ProjectRead


class IncidentCostTypeUpdate(IncidentCostTypeBase):
    id: PrimaryKey = None


class IncidentCostTypeRead(IncidentCostTypeBase):
    id: PrimaryKey


class IncidentCostTypePagination(Pagination):
    items: list[IncidentCostTypeRead] = []
