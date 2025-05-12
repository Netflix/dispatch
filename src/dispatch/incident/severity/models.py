"""Models for incident severity resources in the Dispatch application."""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.event import listen
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.models import DispatchBase, NameStr, ProjectMixin, PrimaryKey, Pagination
from dispatch.project.models import ProjectRead

class IncidentSeverity(Base, ProjectMixin):
    """SQLAlchemy model for incident severity resources."""
    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    color = Column(String)
    enabled = Column(Boolean, default=True)
    default = Column(Boolean, default=False)
    allowed_for_stable_incidents = Column(Boolean, default=True, server_default="t")

    # This column is used to control how severities should be displayed
    # Lower numbers will be shown first.
    view_order = Column(Integer, default=9999)

    search_vector = Column(
        TSVectorType(
            "name",
            "description",
            regconfig="pg_catalog.simple",
        )
    )


listen(IncidentSeverity.default, "set", ensure_unique_default_per_project)


# Pydantic models
class IncidentSeverityBase(DispatchBase):
    """Base Pydantic model for incident severity resources."""
    color: str | None = None
    default: bool | None = None
    description: str | None = None
    enabled: bool | None = None
    name: NameStr
    project: ProjectRead | None = None
    view_order: int | None = None
    allowed_for_stable_incidents: bool | None = None


class IncidentSeverityCreate(IncidentSeverityBase):
    """Pydantic model for creating an incident severity resource."""
    pass


class IncidentSeverityUpdate(IncidentSeverityBase):
    """Pydantic model for updating an incident severity resource."""
    pass


class IncidentSeverityRead(IncidentSeverityBase):
    """Pydantic model for reading an incident severity resource."""
    id: PrimaryKey


class IncidentSeverityReadMinimal(DispatchBase):
    """Pydantic model for reading a minimal incident severity resource."""
    id: PrimaryKey
    color: str | None = None
    default: bool | None = None
    description: str | None = None
    enabled: bool | None = None
    name: NameStr
    allowed_for_stable_incidents: bool | None = None


class IncidentSeverityPagination(Pagination):
    """Pydantic model for paginated incident severity results."""
    items: list[IncidentSeverityRead] = []
