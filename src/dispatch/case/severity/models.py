"""Models and schemas for the Dispatch case severity system."""

from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.sql.schema import UniqueConstraint
from sqlalchemy.event import listen
from sqlalchemy_utils import TSVectorType

from dispatch.database.core import Base, ensure_unique_default_per_project
from dispatch.models import DispatchBase, NameStr, ProjectMixin, PrimaryKey, Pagination
from dispatch.project.models import ProjectRead


class CaseSeverity(Base, ProjectMixin):
    """SQLAlchemy model for a case severity, representing the severity level of a case."""

    __table_args__ = (UniqueConstraint("name", "project_id"),)
    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    color = Column(String)
    enabled = Column(Boolean, default=True)
    default = Column(Boolean, default=False)

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


listen(CaseSeverity.default, "set", ensure_unique_default_per_project)


# Pydantic models
class CaseSeverityBase(DispatchBase):
    """Base Pydantic model for case severity data."""

    color: str | None = None
    default: bool | None = None
    description: str | None = None
    enabled: bool | None = None
    name: NameStr
    project: ProjectRead | None = None
    view_order: int | None = None


class CaseSeverityCreate(CaseSeverityBase):
    """Pydantic model for creating a new case severity."""

    pass


class CaseSeverityUpdate(CaseSeverityBase):
    """Pydantic model for updating a case severity."""

    pass


class CaseSeverityRead(CaseSeverityBase):
    """Pydantic model for reading case severity data."""

    id: PrimaryKey


class CaseSeverityPagination(Pagination):
    """Pydantic model for paginated case severity results."""

    items: list[CaseSeverityRead] = []
