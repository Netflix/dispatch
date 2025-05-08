from datetime import datetime

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
    """SQLAlchemy model for incident cost type resources."""
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
    """Base Pydantic model for incident cost type resources."""
    name: NameStr
    description: str | None = None
    category: str | None = None
    details: dict[str, object] | None = None
    default: bool | None = None
    editable: bool | None = None


class IncidentCostTypeCreate(IncidentCostTypeBase):
    """Pydantic model for creating an incident cost type."""
    project: ProjectRead


class IncidentCostTypeUpdate(IncidentCostTypeBase):
    """Pydantic model for updating an incident cost type."""
    id: PrimaryKey | None = None


class IncidentCostTypeRead(IncidentCostTypeBase):
    """Pydantic model for reading an incident cost type."""
    id: PrimaryKey
    created_at: datetime


class IncidentCostTypePagination(Pagination):
    """Pydantic model for paginated incident cost type results."""
    items: list[IncidentCostTypeRead] = []
