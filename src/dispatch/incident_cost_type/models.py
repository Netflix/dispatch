from datetime import datetime
from typing import List, Optional

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.event import listen

from sqlalchemy_utils import TSVectorType, JSONType

from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.models import DispatchBase, ProjectMixin, TimeStampMixin
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
    name: str
    description: Optional[str]
    category: Optional[str]
    details: Optional[dict] = {}
    created_at: Optional[datetime]
    default: Optional[bool]
    editable: Optional[bool]


class IncidentCostTypeCreate(IncidentCostTypeBase):
    project: ProjectRead


class IncidentCostTypeUpdate(IncidentCostTypeBase):
    id: int


class IncidentCostTypeRead(IncidentCostTypeBase):
    id: int


class IncidentCostTypeNested(IncidentCostTypeBase):
    id: int


class IncidentCostTypePagination(DispatchBase):
    total: int
    items: List[IncidentCostTypeRead] = []
